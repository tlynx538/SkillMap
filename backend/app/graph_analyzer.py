import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import matplotlib.pyplot as plt
from app.models import Skill, Edge
import io
import base64
import networkx as nx

def generate_graph_image(skills, edges, analysis):    
    # Create figure and axes explicitly
    fig, ax = plt.subplots(figsize=(10, 8))
    
    try:
        G = nx.Graph()
        
        # Add nodes
        for skill in skills:
            G.add_node(str(skill.id), name=skill.name, depth=skill.depth_score)
        
        # Add edges
        for edge in edges:
            G.add_edge(str(edge.from_skill_id), str(edge.to_skill_id))
        
        # Map node id -> depth (for node sizing)
        skills_map = {str(skill.id): skill.depth_score for skill in skills}
        
        # Assign colors based on analysis
        node_colors = []
        for node in G.nodes():
            if node in analysis["bridge_nodes"]:
                node_colors.append("orange")
            elif node in analysis["isolates"]:
                node_colors.append("gray")
            else:
                # Find cluster index
                cluster_idx = None
                for idx, cluster in enumerate(analysis["clusters"]):
                    if node in cluster:
                        cluster_idx = idx
                        break
                if cluster_idx is not None:
                    palette = ['lightgreen', 'lightblue', 'plum', 'salmon', 'gold']
                    node_colors.append(palette[cluster_idx % len(palette)])
                else:
                    node_colors.append("skyblue")
        
        # Node sizes based on depth
        node_sizes = [30 + (skills_map.get(node, 0) * 5) for node in G.nodes()]
        
        pos = nx.spring_layout(G, seed=42, k=1.5)
        
        # Draw
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', width=1)
        
        labels = {node: next((s.name for s in skills if str(s.id) == node), node) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold')
        
        ax.set_title("Skill Graph (orange = bridges, grey = isolates, node size = depth)")
        ax.axis('off')
        
        # Save to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        return buf
        
    finally:
        # Always close the figure to free memory
        plt.close(fig)

async def analyze_graph(db: AsyncSession):
    # Build graph
    G = nx.Graph()
    
    skills_result = await db.execute(select(Skill))
    skills = skills_result.scalars().all()
    edges_result = await db.execute(select(Edge))
    edges = edges_result.scalars().all()
    
    for skill in skills:
        G.add_node(str(skill.id), name=skill.name, depth=skill.depth_score, recency=skill.recency_score)
    
    for edge in edges:
        G.add_edge(str(edge.from_skill_id), str(edge.to_skill_id),
                   project=edge.project_name, outcome=edge.outcome)
    
    # Connected components
    components = list(nx.connected_components(G))
    clusters = [list(comp) for comp in components if len(comp) >= 2]
    isolates = [node for node in G.nodes() if G.degree(node) == 0]
    
    # Bridge nodes: nodes whose removal increases component count
    bridge_nodes = []
    original_count = nx.number_connected_components(G)
    for node in G.nodes():
        H = G.copy()
        H.remove_node(node)
        if nx.number_connected_components(H) > original_count:
            bridge_nodes.append(node)
    
    return {
        "clusters": clusters,
        "isolates": isolates,
        "bridge_nodes": bridge_nodes,
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges()
    }

async def analyze_graph_from_lists(skills, edges):
    G = nx.Graph()
    for skill in skills:
        G.add_node(str(skill.id), name=skill.name, depth=skill.depth_score, recency=skill.recency_score)
    for edge in edges:
        G.add_edge(str(edge.from_skill_id), str(edge.to_skill_id),
                   project=edge.project_name, outcome=edge.outcome)

    # Node degree – count edges per node
    degrees = dict(G.degree())
    
    total_skills = len(skills)
    skills_with_edges = sum(1 for deg in degrees.values() if deg > 0)
    evidence_density = (skills_with_edges / total_skills * 100) if total_skills > 0 else 0.0
    
    # Build name mapping
    name_map = {str(s.id): s.name for s in skills}
    strongly_evidenced = [name_map[node] for node, deg in degrees.items() if deg > 0]
    weakly_evidenced = [name_map[node] for node, deg in degrees.items() if deg == 0]
    
    # Existing cluster, isolate, bridge logic
    components = list(nx.connected_components(G))
    clusters = [list(comp) for comp in components if len(comp) >= 2]
    isolates = [node for node in G.nodes() if G.degree(node) == 0]
    
    bridge_nodes = []
    original_count = nx.number_connected_components(G)
    for node in G.nodes():
        H = G.copy()
        H.remove_node(node)
        if nx.number_connected_components(H) > original_count:
            bridge_nodes.append(node)
    
    return {
        "clusters": clusters,
        "isolates": isolates,
        "bridge_nodes": bridge_nodes,
        "node_count": total_skills,
        "edge_count": len(edges),
        "skill_coverage_score": total_skills,
        "evidence_density_score": round(evidence_density, 1),
        "strongly_evidenced_skills": strongly_evidenced,
        "weakly_evidenced_skills": weakly_evidenced
    }
