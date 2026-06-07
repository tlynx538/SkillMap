import React, { useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import cytoscape from 'cytoscape';
import type { GraphData, GraphAnalysis } from '../types';
import html2canvas from 'html2canvas';

interface Props {
  graphData: GraphData;
  analysis: GraphAnalysis;
}

export interface GraphCanvasHandle {
  capture: () => Promise<string>;
}

const GraphCanvas = forwardRef<GraphCanvasHandle, Props>(
  ({ graphData, analysis }, ref) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<cytoscape.Core | null>(null);

    useImperativeHandle(ref, () => ({
      capture: async () => {
        if (!containerRef.current) throw new Error('Container not ready');
        const canvas = await html2canvas(containerRef.current);
        return canvas.toDataURL();
      }
    }));

    useEffect(() => {
      if (!containerRef.current) return;

      if (cyRef.current) {
        cyRef.current.destroy();
      }

      const nodes = graphData.nodes.map(node => ({
        data: {
          id: node.id,
          label: node.name,
          depth: node.depth,
          recency: node.recency,
        },
      }));

      const edges = graphData.edges.map(edge => ({
        data: {
          id: `${edge.from}-${edge.to}`,
          source: edge.from,
          target: edge.to,
          label: edge.project,
        },
      }));

      const cy = cytoscape({
        container: containerRef.current,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              label: 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '12px',
              'background-color': (ele: any) => {
                const nodeId = ele.id();
                if (analysis.bridge_nodes.includes(nodeId)) return '#ff9800';
                if (analysis.isolates.includes(nodeId)) return '#9e9e9e';
                for (let i = 0; i < analysis.clusters.length; i++) {
                  if (analysis.clusters[i].includes(nodeId)) {
                    const hues = ['#4caf50', '#2196f3', '#9c27b0', '#ff5722', '#009688'];
                    return hues[i % hues.length];
                  }
                }
                return '#3f51b5';
              },
              width: (ele: any) => 30 + (ele.data('depth') * 6),
              height: (ele: any) => 30 + (ele.data('depth') * 6),
            },
          },
          {
            selector: 'edge',
            style: {
              width: 2,
              'line-color': '#bbb',
              'target-arrow-color': '#bbb',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              label: 'data(label)',
              'font-size': '10px',
              'text-rotation': 'autorotate',
            },
          },
        ],
        layout: {
          name: 'cose',
          idealEdgeLength: 100,
          nodeRepulsion: 4000,
          gravity: 0.25,
          numIter: 1000,
          fit: true,
          padding: 30,
        },
      });

      cyRef.current = cy;

      return () => {
        if (cyRef.current) cyRef.current.destroy();
      };
    }, [graphData, analysis]);

    return (
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Interactive Skill Graph</h3>
        <div className="border rounded-lg overflow-hidden" style={{ height: '600px' }}>
          <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
        </div>
        <div className="flex gap-4 text-xs flex-wrap">
          <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Bridge node (connects clusters)</div>
          <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-gray-500"></span> Isolate (no connections)</div>
          <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500"></span> Cluster 1</div>
          <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-blue-500"></span> Cluster 2</div>
          <div><span className="font-mono">Node size = Depth</span></div>
        </div>
      </div>
    );
  }
);

export default GraphCanvas;