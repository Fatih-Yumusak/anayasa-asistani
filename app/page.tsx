"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Search, Mic, Upload, ArrowUp, Box, Book, Clock } from "lucide-react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Progress State
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState(""); // "Veritabanı taranıyor", "Cevap üretiliyor"

  // PDF Modal State
  const [readerState, setReaderState] = useState<{ targetId: string, source: string } | null>(null);

  // Environment aware API URL
  const API_BASE = process.env.NODE_ENV === 'production' ? '' : "http://localhost:8000";

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse(null);
    setProgress(0);
    setStage("Veritabanı taranıyor...");

    // Simulation Timer for visual feedback
    let progressTimer: NodeJS.Timeout | undefined;
    progressTimer = setInterval(() => {
      setProgress(prev => {
        if (prev < 90) return prev + 2;
        return prev;
      });
    }, 200);

    try {
      // PHASE 1: RETRIEVAL
      // This is now a real network call, ~1-3s
      const retrieveRes = await axios.post(`${API_BASE}/api/retrieve`, { question: query });
      const contextDocs = retrieveRes.data.context_docs || [];

      setProgress(50);

      if (contextDocs.length > 0) {
        setStage(`İlgili ${contextDocs.length} madde bulundu. Cevap ve Harita üretiliyor...`);
      } else {
        setStage("Doğrudan bilgi bulunamadı, genel cevap üretiliyor...");
      }

      // PHASE 2: GENERATION
      // This is another network call, ~2-5s
      // Sending context back to server is stateless and efficient
      const generateRes = await axios.post(`${API_BASE}/api/answer`, {
        question: query,
        context_docs: contextDocs
      });

      // Done
      if (progressTimer) clearInterval(progressTimer);
      setProgress(100);
      setStage("İşlem Tamamlandı.");

      // Construct final response object compatible with UI
      const finalResult = {
        answer: generateRes.data.answer,
        vis_data: generateRes.data.vis_data, // Capture vis_data
        sources: contextDocs.map((doc: any) => ({
          madde: doc.madde_no,
          text: doc.text,
          metadata: doc.metadata,
          score: doc.score
        }))
      };

      setTimeout(() => {
        setResponse(finalResult);
        setLoading(false);
      }, 500);

    } catch (error) {
      if (progressTimer) clearInterval(progressTimer);
      console.error(error);
      alert("Bir hata oluştu. Lütfen tekrar deneyin.");
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };


  return (
    // Main container handled by Layout, just specific page styling here if needed
    <div className="flex-grow flex flex-col font-sans text-gray-800">

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center p-6 relative">

        {/* Intro Text */}
        {!response && !loading && (
          <h1 className="text-2xl md:text-3xl text-gray-700 mb-8 text-center">
            Türk Anayasası mevzuatına yapay zeka desteğiyle erişin.
          </h1>
        )}

        {/* Search Bar */}
        <div className={`w-full max-w-2xl bg-[#EBEBEB] rounded-2xl shadow-lg p-2 transition-all duration-500 ${response || loading ? 'mt-0' : 'mb-12'}`}>
          <div className="flex flex-col relative">
            <textarea
              className="w-full bg-transparent p-4 min-h-[60px] outline-none text-gray-700 placeholder-gray-500 resize-none"
              placeholder="Sorunuzu sorun..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <div className="flex justify-end items-center px-2 pb-2">
              <button
                onClick={handleSearch}
                disabled={loading}
                className={`p-2 rounded-full transition ${query ? 'bg-black text-white' : 'bg-gray-300 text-gray-500'}`}
              >
                <ArrowUp size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Loading State - Deterministic Progress Bar */}
        {loading && (
          <div className="w-full max-w-2xl mt-8 px-2 fade-in">
            <div className="flex justify-between text-xs text-gray-600 mb-2 font-medium">
              <span>{stage}</span>
              <span>%{Math.round(progress)}</span>
            </div>

            <div className="h-2 w-full bg-gray-300 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-red-600 to-red-400 transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>

            <p className="text-center text-[10px] text-gray-400 mt-2">
              Google Gemini AI altyapısı kullanılarak yanıt ve analiz haritası üretiliyor.
            </p>
          </div>
        )}

        {/* Results Area */}
        {response && (
          <div className="w-full max-w-4xl bg-white rounded-xl shadow-xl p-8 mt-8 fade-in">
            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Yanıt</h2>
            <div className="prose max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
              {response.answer}
            </div>

            {response.sources && response.sources.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <Book size={20} className="mr-2 text-red-600" /> Kaynak Maddeler
                </h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {response.sources.map((src: any, idx: number) => {
                    // Determine Source Name safely
                    const sourceName = src.metadata?.source || "Anayasa";

                    return (
                      <div
                        key={idx}
                        onClick={() => {
                          // Set Target ID and Source for Reader
                          // For TIHEK, IDs are like "TIHEK Kanunu MADDE 3"
                          // For Anayasa, IDs are like "MADDE 3"
                          // We pass exact source to filter the reader
                          const targetId = sourceName === "Anayasa" ? `MADDE ${src.madde}` : `${sourceName} MADDE ${src.madde}`;
                          setReaderState({ targetId, source: sourceName });
                        }}
                        className="cursor-pointer block bg-gray-50 border-l-4 border-red-500 p-4 rounded text-sm hover:shadow-md transition hover:bg-red-50 group"
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-red-700 group-hover:text-red-900">
                            {/* Display user friendly name */}
                            {sourceName === "Anayasa" ? `MADDE ${src.madde}` : `${sourceName} Md. ${src.madde}`}
                          </span>
                          <span className="text-xs text-gray-400 font-mono border px-1 rounded flex items-center gap-1">
                            <Book size={10} /> Sayfa {src.metadata?.page || "?"} (Oku)
                          </span>
                        </div>
                        {/* Show Source Badge if not Anayasa */}
                        {sourceName !== "Anayasa" && (
                          <span className="inline-block bg-blue-100 text-blue-800 text-[10px] px-2 py-0.5 rounded-full mb-2 font-semibold">
                            {sourceName}
                          </span>
                        )}
                        <p className="line-clamp-4 text-gray-600">{src.text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Semantic Map */}
            {response.vis_data ? (
              <EmbeddingMap visData={response.vis_data} />
            ) : (
              <div className="mt-8 border-t pt-4 text-center">
                <p className="text-xs text-gray-400 bg-gray-50 p-2 rounded inline-block">
                  ⚠️ Anlamsal Analiz Haritası verisi yüklenemedi. (Backend veri dönüşü boş)
                </p>
              </div>
            )}
          </div>
        )}

        {/* Feature Cards */}
        {!response && !loading && (
          <div className="grid md:grid-cols-3 gap-6 w-full max-w-5xl px-4 mt-8">
            <FeatureCard
              icon={<Box size={24} className="text-white" />}
              title="Yapay Zeka Destekli"
              desc="Modern AI teknolojisiyle hızlı ve doğru sonuçlar"
            />
            <FeatureCard
              icon={<Book size={24} className="text-white" />}
              title="Kapsamlı Mevzuat"
              desc="Anayasa belgelerinin tamamı"
              color="bg-yellow-500"
            />
            <FeatureCard
              icon={<Clock size={24} className="text-white" />}
              title="Anında Erişim"
              desc="İhtiyacınız olan bilgiye saniyeler içinde ulaşın"
              color="bg-red-600"
            />
          </div>
        )}

      </main>

      {/* Legislation Reader Modal */}
      {readerState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 fade-in">
          <div className="bg-white w-full h-full max-w-5xl rounded-xl shadow-2xl flex flex-col overflow-hidden relative">
            {/* Header */}
            <div className="bg-gray-100 p-4 border-b flex justify-between items-center shadow-sm z-10">
              <div className="flex items-center space-x-2">
                <Book size={20} className="text-red-600" />
                <span className="font-bold text-gray-700">
                  {readerState.source} - Mevzuat Okuyucu
                </span>
              </div>
              <button
                onClick={() => setReaderState(null)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-full transition font-medium"
              >
                ✕ Kapat
              </button>
            </div>

            {/* Reader Content */}
            <LegislationReader targetId={readerState.targetId} source={readerState.source} />

            {/* Tip */}
            <div className="bg-yellow-50 text-yellow-800 text-xs p-2 text-center border-t">
              İlgili madde otomatik olarak vurgulanmıştır.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function LegislationReader({ targetId, source }: { targetId: string, source: string }) {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    // Fetch filtered text
    setLoading(true);
    axios.get(`${API_BASE}/api/legislation`, { params: { source } })
      .then(res => {
        setArticles(res.data.articles);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load legislation", err);
        setLoading(false);
      });
  }, [source]); // Re-fetch when source changes

  // Auto-Scroll Effect
  useEffect(() => {
    if (!loading && targetId && articles.length > 0) {
      // Small delay to ensure rendering
      setTimeout(() => {
        const element = document.getElementById(targetId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 300);
    }
  }, [loading, targetId, articles]);

  if (loading) return <div className="flex-1 flex items-center justify-center">Yükleniyor...</div>;

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-white space-y-8">
      {articles.length === 0 && (
        <div className="text-center text-gray-500">Bu belge için içerik bulunamadı.</div>
      )}
      {articles.map((article: any) => {
        const isTarget = article.id === targetId;
        // Parse Text: Remove "KONU: ..." line if present to make it cleaner
        const cleanText = article.text.replace(/^KONU:.*\n/, "");

        return (
          <div
            key={article.id}
            id={article.id} // use unique ID (includes source if needed)
            className={`p-6 rounded-lg transition-all duration-1000 ${isTarget ? 'bg-yellow-100 ring-4 ring-yellow-400 shadow-xl scale-[1.02]' : 'hover:bg-gray-50'}`}
          >
            <div className="flex items-baseline space-x-3 mb-2">
              <span className={`font-bold text-lg ${isTarget ? 'text-red-700' : 'text-gray-800'}`}>
                {/* Display Number cleanly */}
                MADDE {article.madde_no}
              </span>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
                {article.metadata.konu}
              </span>
            </div>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap text-justify border-l-4 border-gray-200 pl-4">
              {cleanText}
            </p>
          </div>
        );
      })}
    </div>
  );
}


// Interactive Map Component
function EmbeddingMap({ visData }: { visData: any }) {
  if (!visData || !visData.map_points) return null;

  const points = visData.map_points;
  const query = visData.query_point;

  // Zoom / Pan State
  const [scale, setScale] = useState(1);
  const [panning, setPanning] = useState({ x: 0, y: 0 }); // Offset
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const textVisible = scale > 1.5; // Show labels earlier

  // Base dimensions
  const w = 600;
  const h = 400;

  // Smart Zoom: Zooms towards the center of the current view
  const applyZoom = (factor: number) => {
    const newScale = Math.min(Math.max(scale * factor, 1), 10);
    if (newScale === scale) return;

    // Calculate center of view
    // Current center in data coordinates:
    // (w/2 - pan_x) / scale
    const centerX = (w / 2 - panning.x) / scale;
    const centerY = (h / 2 - panning.y) / scale;

    // Calculate new pan to keep center fixed
    // new_pan = w/2 - centerX * newScale
    const newPanX = w / 2 - centerX * newScale;
    const newPanY = h / 2 - centerY * newScale;

    setScale(newScale);
    setPanning({ x: newPanX, y: newPanY });
  };

  const zoomIn = () => applyZoom(1.5);
  const zoomOut = () => applyZoom(1 / 1.5);
  const resetZoom = () => {
    setScale(1);
    setPanning({ x: 0, y: 0 });
  };

  const handleWheel = (e: React.WheelEvent) => {
    // Prevent page scroll only if we decide to capture it (optional)
    // e.preventDefault(); 
    // Implementation of simple zoom on wheel is tricky without blocking scroll.
    // Let's stick to buttons for main control for better UX on long page.
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panning.x, y: e.clientY - panning.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    e.preventDefault();
    setPanning({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="mt-8 border-t pt-8">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <Box size={20} className="mr-2 text-indigo-600" /> Anlamsal Analiz Haritası
        </h3>
        {/* Controls */}
        <div className="flex space-x-2 bg-gray-100 rounded-lg p-1 border">
          <button onClick={zoomIn} className="w-8 h-8 flex items-center justify-center bg-white rounded shadow-sm hover:bg-gray-50 font-bold text-gray-700" title="Yakınlaş">＋</button>
          <button onClick={zoomOut} className="w-8 h-8 flex items-center justify-center bg-white rounded shadow-sm hover:bg-gray-50 font-bold text-gray-700" title="Uzaklaş">－</button>
          <button onClick={resetZoom} className="px-3 h-8 flex items-center justify-center bg-white rounded shadow-sm hover:bg-gray-50 text-xs font-semibold text-gray-600" title="Haritayı Sıfırla">Sıfırla</button>
        </div>
      </div>

      <div
        className="relative w-full aspect-video bg-gray-50 rounded-xl border overflow-hidden shadow-inner cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* SVG Plot */}
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full select-none">
          {/* Semantic Zoom Transform Group */}
          <g transform={`translate(${panning.x}, ${panning.y}) scale(${scale})`}>

            {/* Background Grid (Fixed relative to data, moves with pan/zoom) */}
            <line x1="0" y1={h / 2} x2={w} y2={h / 2} stroke="#ddd" strokeWidth={1 / scale} strokeDasharray="4 4" />
            <line x1={w / 2} y1="0" x2={w / 2} y2={h} stroke="#ddd" strokeWidth={1 / scale} strokeDasharray="4 4" />

            {/* Document Points */}
            {points.map((p: any, idx: number) => {
              const color = (p.source && p.source.includes("Anayasa")) ? "#ef4444" : "#3b82f6";
              return (
                <g key={idx} transform={`translate(${p.x * w}, ${p.y * h})`}>
                  <circle
                    r={3 / Math.sqrt(scale)} // Keep dots constant physical size or slightly smaller
                    fill={color}
                    opacity={0.6}
                    className="hover:opacity-100 transition-opacity"
                  />
                  {/* Conditional Label */}
                  {textVisible && (
                    <text
                      x={4 / scale}
                      y={2 / scale}
                      fontSize={12 / scale} // Larger font size
                      fontWeight="bold"
                      fill="#333"
                      pointerEvents="none"
                      style={{
                        textShadow:
                          `1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff`
                      }}
                    >
                      {p.madde}
                    </text>
                  )}
                  <title>{p.source} - Madde {p.madde}</title>
                </g>
              );
            })}

            {/* Query Point - Professional Marker */}
            {query && (
              <g transform={`translate(${query.x * w}, ${query.y * h})`}>
                {/* Precise Center Point */}
                <circle r={4 / scale} fill="#000000" stroke="#ffffff" strokeWidth={1.5 / scale} />

                {/* Outer Ring (Static) */}
                <circle r={12 / scale} fill="none" stroke="#000000" strokeWidth={1 / scale} opacity="0.3" strokeDasharray="2 2" />

                {/* Label */}
                <text x={8 / scale} y={4 / scale} fontSize={10 / scale} fontWeight="bold" fill="#000000" style={{ textShadow: "0px 0px 4px white" }}>
                  Sorgu Konumu
                </text>
              </g>
            )}

          </g> {/* End Transform Group */}


          {/* Static Legend (Stays fixed on screen, outside transform) */}
          <g transform="translate(20, 20)">
            <rect x="-5" y="-5" width="100" height="60" fill="white" opacity="0.8" rx="4" />

            <circle cx="0" cy="0" r="4" fill="#ef4444" opacity="0.6" />
            <text x="10" y="4" fontSize="10" fill="#666">Anayasa</text>

            <circle cx="0" cy="15" r="4" fill="#3b82f6" opacity="0.6" />
            <text x="10" y="19" fontSize="10" fill="#666">İnsan Hakları</text>

            {/* Query Legend Item */}
            <circle cx="0" cy="35" r="3" fill="#000000" stroke="#fff" strokeWidth="1" />
            <text x="12" y="38" fontSize="10" fontWeight="bold" fill="#000">Sorgu</text>
          </g>
        </svg>

        <p className="absolute bottom-2 right-2 text-[10px] text-gray-400 bg-white/80 px-2 rounded pointer-events-none">
          Scale: {scale.toFixed(1)}x
        </p>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc, color = "bg-red-600" }: { icon: any, title: string, desc: string, color?: string }) {
  return (
    <div className="bg-[#EBEBEB] p-6 rounded-xl flex flex-col items-center text-center shadow-sm hover:shadow-md transition">
      <div className={`p-4 rounded-xl mb-4 ${color}`}>
        {icon}
      </div>
      <h3 className="font-bold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{desc}</p>
    </div>
  )
}

