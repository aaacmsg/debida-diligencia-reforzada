import { useState, useEffect, useCallback, useRef } from 'react';
import { ZoomIn, ZoomOut, RefreshCw, Play } from 'lucide-react';
import { grafoService } from '../services/grafoService';
import type { GraphData, GraphNode, GraphEdge } from '../types';

const COLORS = {
  cliente: '#3b82f6',
  empresa: '#8b5cf6',
  persona: '#10b981',
  documento: '#64748b',
  riesgoAlto: '#ef4444',
  riesgoMedio: '#eab308',
  riesgoBajo: '#22c55e',
  peo: '#f97316',
  edge: '#94a3b8',
};

interface NodePosition {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  pinned?: boolean;
}

function forceSimulation(
  nodes: GraphNode[],
  edges: GraphEdge[],
  width: number,
  height: number,
  iterations = 100
): Record<string, NodePosition> {
  const positions: Record<string, NodePosition> = {};
  const centerX = width / 2;
  const centerY = height / 2;

  nodes.forEach((node, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI;
    const r = Math.min(width, height) * 0.3;
    positions[node.id] = {
      id: node.id,
      x: centerX + r * Math.cos(angle) + (Math.random() - 0.5) * 50,
      y: centerY + r * Math.sin(angle) + (Math.random() - 0.5) * 50,
      vx: 0,
      vy: 0,
    };
  });

  const REPULSION = 5000;
  const ATTRACTION = 0.005;
  const DAMPING = 0.85;
  const CENTERING = 0.01;

  for (let iter = 0; iter < iterations; iter++) {
    const cooling = 1 - iter / iterations;

    for (const id in positions) {
      if (positions[id].pinned) continue;
      let fx = 0;
      let fy = 0;

      for (const otherId in positions) {
        if (id === otherId) continue;
        const dx = positions[id].x - positions[otherId].x;
        const dy = positions[id].y - positions[otherId].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = REPULSION / (dist * dist);
        fx += (dx / dist) * force;
        fy += (dy / dist) * force;
      }

      fx += (centerX - positions[id].x) * CENTERING;
      fy += (centerY - positions[id].y) * CENTERING;

      positions[id].vx = (positions[id].vx + fx) * DAMPING;
      positions[id].vy = (positions[id].vy + fy) * DAMPING;
      positions[id].x += positions[id].vx * cooling;
      positions[id].y += positions[id].vy * cooling;
    }

    for (const edge of edges) {
      const s = positions[edge.source];
      const t = positions[edge.target];
      if (!s || !t) continue;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - 100) * ATTRACTION;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      if (!s.pinned) { s.vx += fx; s.vy += fy; }
      if (!t.pinned) { t.vx -= fx; t.vy -= fy; }
    }
  }

  return positions;
}

export default function GrafoPage() {
  const [graphData, setGraphData] = useState<GraphData>({
    nodes: [],
    edges: [],
  });
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState<string | null>(null);
  const [positions, setPositions] = useState<Record<string, NodePosition>>({});
  const [simulating, setSimulating] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    setLoading(true);
    try {
      const data = await grafoService.getGrafo();
      setGraphData(data);
      runSimulation(data.nodes, data.edges);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = (nodes: GraphNode[], edges: GraphEdge[]) => {
    setSimulating(true);
    const svg = svgRef.current;
    const w = svg ? svg.clientWidth : 800;
    const h = svg ? svg.clientHeight : 600;
    const newPositions = forceSimulation(nodes, edges, w, h, 150);
    setPositions(newPositions);
    setTimeout(() => setSimulating(false), 100);
  };

  const getNodeColor = (node: GraphNode) => {
    if (node.es_pep) return COLORS.peo;
    if (node.type === 'empresa') return COLORS.empresa;
    if (node.type === 'persona') return COLORS.persona;
    if (node.type === 'documento') return COLORS.documento;
    if (node.riesgo === 'alto') return COLORS.riesgoAlto;
    if (node.riesgo === 'medio') return COLORS.riesgoMedio;
    if (node.riesgo === 'bajo') return COLORS.riesgoBajo;
    return COLORS.cliente;
  };

  const handleMouseDown = (nodeId: string) => {
    setDragging(nodeId);
    setPositions(prev => ({
      ...prev,
      [nodeId]: { ...prev[nodeId], pinned: true },
    }));
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return;

    const svg = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - svg.left - offset.x) / zoom;
    const y = (e.clientY - svg.top - offset.y) / zoom;

    setPositions((prev) => ({
      ...prev,
      [dragging]: { ...prev[dragging], x, y },
    }));
  }, [dragging, offset, zoom]);

  const handleMouseUp = () => {
    setDragging(null);
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setOffset({ x: 0, y: 0 });
    runSimulation(graphData.nodes, graphData.edges);
  };
  const handleReRun = () => {
    setPositions({});
    runSimulation(graphData.nodes, graphData.edges);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grafo de Relaciones</h1>
          <p className="text-gray-500">Visualizacion de vinculos entre clientes y empresas</p>
        </div>
      </div>

      {/* Toolbar */}
      <div className="card flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button onClick={handleZoomIn} aria-label="Acercar" className="p-2 hover:bg-gray-100 rounded-lg">
            <ZoomIn className="w-5 h-5" />
          </button>
          <button onClick={handleZoomOut} aria-label="Alejar" className="p-2 hover:bg-gray-100 rounded-lg">
            <ZoomOut className="w-5 h-5" />
          </button>
          <button onClick={handleReset} aria-label="Restablecer vista" className="p-2 hover:bg-gray-100 rounded-lg">
            <RefreshCw className="w-5 h-5" />
          </button>
          <button onClick={handleReRun} disabled={simulating} aria-label="Recalcular simulacion" className="p-2 hover:bg-gray-100 rounded-lg">
            <Play className={`w-5 h-5 ${simulating ? 'animate-spin' : ''}`} />
          </button>
          <span className="text-sm text-gray-500">
            Zoom: {(zoom * 100).toFixed(0)}% | {graphData.nodes.length} nodos, {graphData.edges.length} aristas
          </span>
        </div>
        <div data-testid="grafo-leyenda" className="flex items-center space-x-4 text-xs text-gray-600">
          <span className="font-medium">Leyenda:</span>
          {[
            { color: COLORS.cliente, label: 'Cliente' },
            { color: COLORS.peo, label: 'PEP' },
            { color: COLORS.persona, label: 'Persona' },
            { color: COLORS.documento, label: 'Documento' },
          ].map((item) => (
            <span key={item.label} className="flex items-center">
              <span
                className="w-3 h-3 rounded-full mr-1.5 inline-block"
                style={{ backgroundColor: item.color }}
              />
              {item.label}
            </span>
          ))}
        </div>
      </div>

      {/* Graph */}
      <div className="card overflow-hidden" style={{ height: '600px' }}>
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <g transform={`translate(${offset.x}, ${offset.y}) scale(${zoom})`}>
            {/* Edges */}
            {graphData.edges.map((edge, index) => {
              const source = positions[edge.source];
              const target = positions[edge.target];
              if (!source || !target) return null;

              const midX = (source.x + target.x) / 2;
              const midY = (source.y + target.y) / 2;

              return (
                <g key={`edge-${index}`}>
                  <line
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke={COLORS.edge}
                    strokeWidth={2}
                  />
                  {edge.label && (
                    <text
                      x={midX}
                      y={midY - 5}
                      textAnchor="middle"
                      className="text-xs fill-gray-600"
                    >
                      {edge.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {graphData.nodes.map((node) => {
              const pos = positions[node.id];
              if (!pos) return null;

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onMouseDown={() => handleMouseDown(node.id)}
                  className="cursor-pointer"
                >
                  <circle
                    r={node.es_pep ? 35 : 30}
                    fill={getNodeColor(node)}
                    stroke="white"
                    strokeWidth={3}
                    filter="url(#shadow)"
                  />
                  <text
                    textAnchor="middle"
                    dy="0.35em"
                    className="text-xs fill-white font-medium pointer-events-none"
                  >
                    {node.label.length > 12
                      ? node.label.substring(0, 12) + '...'
                      : node.label}
                  </text>
                  {node.es_pep && (
                    <text
                      y={-45}
                      textAnchor="middle"
                      className="text-xs fill-red-600 font-bold"
                    >
                      PEP
                    </text>
                  )}
                </g>
              );
            })}

            <defs>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.2" />
              </filter>
            </defs>
          </g>
        </svg>
      </div>

      {/* Legend */}
      <div className="card">
        <h3 className="font-semibold mb-4">Leyenda</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.cliente }}></div>
            <span className="text-sm">Cliente</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.empresa }}></div>
            <span className="text-sm">Empresa</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.persona }}></div>
            <span className="text-sm">Persona</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.documento }}></div>
            <span className="text-sm">Documento</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.peo }}></div>
            <span className="text-sm">PEP</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.riesgoAlto }}></div>
            <span className="text-sm">Riesgo Alto</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.riesgoMedio }}></div>
            <span className="text-sm">Riesgo Medio</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS.riesgoBajo }}></div>
            <span className="text-sm">Riesgo Bajo</span>
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-4">
          Arrastra nodos para reposicionarlos. Usa el boton Play para re-ejecutar la simulacion de fuerzas.
        </p>
      </div>
    </div>
  );
}
