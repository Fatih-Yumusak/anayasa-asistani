import React from 'react';
import { Scale, Heart, Shield, Award } from 'lucide-react';

export default function AboutPage() {
    return (
        <div className="flex-grow flex flex-col items-center p-8 md:p-16 space-y-12 max-w-5xl mx-auto">

            {/* Hero Section */}
            <div className="text-center space-y-4">
                <div className="inline-block p-4 bg-red-100 rounded-full mb-4">
                    <Scale size={48} className="text-red-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-800">Proje Hakkında</h1>
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                    Anayasa AI, Türk hukuk mevzuatını yapay zeka teknolojisiyle herkes için erişilebilir, anlaşılır ve şeffaf kılmayı amaçlayan bir sosyal sorumluluk projesidir.
                </p>
            </div>

            {/* Mission Content */}
            <div className="grid md:grid-cols-2 gap-8 w-full">
                <div className="bg-white p-8 rounded-2xl shadow-lg border-l-8 border-red-500">
                    <Heart size={32} className="text-red-500 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Vizyonumuz</h2>
                    <p className="text-gray-600 leading-relaxed">
                        Hukuk kuralları toplumun her bireyini bağlar; ancak bu kuralların dili genellikle karmaşıktır. Amacımız, bu karmaşıklığı ortadan kaldırarak her vatandaşın haklarını ve sorumluluklarını saniyeler içinde öğrenebilmesini sağlamaktır.
                    </p>
                </div>

                <div className="bg-white p-8 rounded-2xl shadow-lg border-l-8 border-yellow-400">
                    <Shield size={32} className="text-yellow-500 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Güvenilirlik</h2>
                    <p className="text-gray-600 leading-relaxed">
                        Yapay zekanın "halüsinasyon" riskini minimize etmek için RAG teknolojisi kullanıyoruz. Cevaplarımız asla uydurma değildir; her kelimesi T.C. Anayasası'nın ilgili maddelerine dayandırılır ve kaynaklarıyla birlikte sunulur.
                    </p>
                </div>
            </div>

            {/* Credits */}
            <div className="bg-gray-200 rounded-xl p-6 w-full text-center">
                <p className="text-gray-700">
                    Bu proje <span className="font-bold text-red-700">Google DeepMind</span> desteğiyle Fatih Yumusak tarafından geliştirilmiştir.
                </p>
            </div>
        </div>
    );
}
