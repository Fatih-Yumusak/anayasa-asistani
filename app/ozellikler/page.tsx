import React from 'react';
import { Cpu, Search, Database, Lock, Zap, BookOpen } from 'lucide-react';

export default function FeaturesPage() {
    return (
        <div className="flex-grow flex flex-col items-center p-8 md:p-16 max-w-6xl mx-auto">
            <h1 className="text-4xl font-bold text-gray-800 mb-12 text-center">Teknik Özellikler</h1>

            <div className="grid md:grid-cols-3 gap-6 w-full">

                <TechCard
                    icon={<Cpu />}
                    title="Gelişmiş LLM"
                    desc="Qwen2.5-1.5B-Instruct modeli, düşük gecikme süresi ile yüksek doğrulukta Türkçe yanıtlar üretir."
                />

                <TechCard
                    icon={<Search />}
                    title="RAG Mimarisi"
                    desc="Retrieval-Augmented Generation (RAG) ile sadece veri tabanındaki gerçek belgelerden bilgi çeker."
                    color="text-blue-600"
                />

                <TechCard
                    icon={<Database />}
                    title="Vektör Arama"
                    desc="ChromaDB ve multilingual-e5-base embedding modeli ile kelime değil, anlam bazlı arama yapar."
                    color="text-green-600"
                />

                <TechCard
                    icon={<Lock />}
                    title="Constitutional AI"
                    desc="Sistem, anayasal değerlere aykırı veya zararlı içerik üretmeyecek şekilde sınırlandırılmıştır."
                    color="text-purple-600"
                />

                <TechCard
                    icon={<Zap />}
                    title="Hızlı Yanıt"
                    desc="Optimize edilmiş retrieval pipeline sayesinde sorgular milisaniyeler içinde işlenir."
                    color="text-yellow-600"
                />

                <TechCard
                    icon={<BookOpen />}
                    title="Akıllı Mevzuat"
                    desc="Tıklanabilir kaynak kartları ve mevzuat okuyucu ile belgenin orijinaline anında erişim."
                    color="text-red-600"
                />

            </div>
        </div>
    );
}

function TechCard({ icon, title, desc, color = "text-gray-800" }: { icon: any, title: string, desc: string, color?: string }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition duration-300 border border-gray-100 flex flex-col items-start">
            <div className={`p-3 bg-gray-50 rounded-lg mb-4 ${color}`}>
                {React.cloneElement(icon, { size: 32 })}
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{desc}</p>
        </div>
    );
}
