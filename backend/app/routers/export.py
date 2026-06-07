from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from uuid import UUID
from app.database import get_db
from app.models import Skill, Edge, Artifact, Resume
from app.graph_analyzer import analyze_graph_from_lists, generate_graph_image
from app.schemas import ExportRequest   # ✅ define this in schemas.py (see below)

router = APIRouter(prefix="/api/export", tags=["export"])

@router.post("/pdf")
async def export_pdf(
    resume_id: UUID = Query(...),
    req: ExportRequest = None,
    db: AsyncSession = Depends(get_db)
):
    # Verify resume exists
    resume_result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = resume_result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Fetch skills and edges
    skills = (await db.execute(select(Skill).where(Skill.resume_id == resume_id))).scalars().all()
    edges = (await db.execute(select(Edge).where(Edge.resume_id == resume_id))).scalars().all()
    
    # Get analysis (clusters, bridges, isolates)
    analysis = await analyze_graph_from_lists(skills, edges)
    
    # ---------- PDF BUILDING ----------
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Title
    resume_title = resume.name if resume.name else f"Resume from {resume.created_at.strftime('%Y-%m-%d %H:%M')}"
    story.append(Paragraph(f"Engineer Skill Map Report: {resume_title}", title_style))
    story.append(Spacer(1, 0.25*inch))
    
    # ---------- Graph Image (use screenshot if provided, else generate) ----------
    story.append(Paragraph("Skill Graph Visualization", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    if req and req.graph_image:
        # Use frontend screenshot
        try:
            image_data = req.graph_image.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            img = Image(BytesIO(image_bytes), width=6*inch, height=5*inch)
            story.append(img)
        except Exception as e:
            # Fallback to generated image if screenshot fails
            graph_img_buf = generate_graph_image(skills, edges, analysis)
            story.append(Image(graph_img_buf, width=6*inch, height=5*inch))
    else:
        # Use matplotlib generated image
        graph_img_buf = generate_graph_image(skills, edges, analysis)
        story.append(Image(graph_img_buf, width=6*inch, height=5*inch))
    story.append(Spacer(1, 0.3*inch))
    
    # ---------- Metrics ----------
    story.append(Paragraph("Skill Evidence Metrics", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Skill Coverage Score: {analysis['skill_coverage_score']} skills", normal_style))
    story.append(Paragraph(f"Evidence Density Score: {analysis['evidence_density_score']}% ({analysis['edge_count']} edges)", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Strongly Evidenced Skills", heading_style))
    if analysis["strongly_evidenced_skills"]:
        story.append(Paragraph(", ".join(analysis["strongly_evidenced_skills"]), normal_style))
    else:
        story.append(Paragraph("None", normal_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Weakly Evidenced Skills (need stronger narratives)", heading_style))
    if analysis["weakly_evidenced_skills"]:
        story.append(Paragraph(", ".join(analysis["weakly_evidenced_skills"]), normal_style))
    else:
        story.append(Paragraph("All skills are evidenced – great!", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ---------- Skills Table ----------
    story.append(Paragraph("All Skills (with Depth & Recency)", heading_style))
    story.append(Spacer(1, 0.1*inch))
    skill_data = [["Skill", "Depth", "Recency"]]
    for s in skills:
        skill_data.append([s.name, str(s.depth_score), str(s.recency_score)])
    skill_table = Table(skill_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch])
    skill_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(skill_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ---------- Clusters ----------
    story.append(Paragraph("Tight Clusters (Areas of Depth)", heading_style))
    story.append(Spacer(1, 0.1*inch))
    if analysis["clusters"]:
        for idx, cluster in enumerate(analysis["clusters"], 1):
            skill_names = [next((s.name for s in skills if str(s.id) == n), n) for n in cluster]
            cluster_text = f"<b>Cluster {idx}:</b> " + ", ".join(skill_names)
            story.append(Paragraph(cluster_text, normal_style))
            story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph("No clusters detected. Add more edges.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ---------- Bridge Nodes ----------
    story.append(Paragraph("Bridge Nodes (Cross-Domain Leverage)", heading_style))
    story.append(Spacer(1, 0.1*inch))
    if analysis["bridge_nodes"]:
        bridge_names = [next((s.name for s in skills if str(s.id) == n), n) for n in analysis["bridge_nodes"]]
        story.append(Paragraph(", ".join(bridge_names), normal_style))
    else:
        story.append(Paragraph("No bridge nodes detected.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ---------- Isolates ----------
    story.append(Paragraph("Isolates (Unconnected Skills)", heading_style))
    story.append(Spacer(1, 0.1*inch))
    if analysis["isolates"]:
        isolate_names = [next((s.name for s in skills if str(s.id) == n), n) for n in analysis["isolates"]]
        story.append(Paragraph(", ".join(isolate_names), normal_style))
    else:
        story.append(Paragraph("No isolates – great connectivity!", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # ---------- Edges Table ----------
    story.append(Paragraph("Skill Edges (Projects & Outcomes)", heading_style))
    story.append(Spacer(1, 0.1*inch))
    if edges:
        edge_data = [["Skill A", "Skill B", "Project", "Outcome"]]
        for e in edges:
            from_skill = next((s for s in skills if s.id == e.from_skill_id), None)
            to_skill = next((s for s in skills if s.id == e.to_skill_id), None)
            if from_skill and to_skill:
                edge_data.append([
                    from_skill.name, to_skill.name,
                    e.project_name, e.outcome[:80] + ("..." if len(e.outcome) > 80 else "")
                ])
        edge_table = Table(edge_data, colWidths=[1.2*inch, 1.2*inch, 1.5*inch, 2.2*inch])
        edge_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(edge_table)
    else:
        story.append(Paragraph("No edges created yet.", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    # Filename
    safe_title = "".join(c for c in resume_title if c.isalnum() or c in (' ', '_')).replace(' ', '_')
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=skill_map_{safe_title}.pdf"}
    )