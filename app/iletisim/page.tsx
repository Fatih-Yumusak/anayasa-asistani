"use client";

import React from 'react';
import { Mail, MapPin, Phone, Github, Twitter } from 'lucide-react';

export default function ContactPage() {
    return (
        <div className="flex-grow flex flex-col items-center justify-center p-8 md:p-16 max-w-4xl mx-auto w-full">
            <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">İletişim</h1>

            <div className="bg-white w-full rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row">

                {/* Info Side */}
                <div className="bg-[#D32F2F] text-white p-10 md:w-2/5 flex flex-col justify-between">
                    <div>
                        <h2 className="text-2xl font-bold mb-6">Bize Ulaşın</h2>
                        <p className="text-red-100 mb-8">
                            Proje hakkında öneri, hata bildirimi veya iş birliği talepleriniz için bize ulaşabilirsiniz.
                        </p>

                        <div className="space-y-4">
                            <div className="flex items-center space-x-3">
                                <Mail size={20} className="text-yellow-400" />
                                <span>iletisim@anayasai.com</span>
                            </div>
                            <div className="flex items-center space-x-3">
                                <Phone size={20} className="text-yellow-400" />
                                <span>+90 555 000 00 00</span>
                            </div>
                            <div className="flex items-center space-x-3">
                                <MapPin size={20} className="text-yellow-400" />
                                <span>İstanbul, Türkiye</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex space-x-4 mt-8">
                        <a href="#" className="hover:text-yellow-400 transition"><Github /></a>
                        <a href="#" className="hover:text-yellow-400 transition"><Twitter /></a>
                    </div>
                </div>

                {/* Form Side (Cosmetic) */}
                <div className="p-10 md:w-3/5 bg-gray-50">
                    <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Adınız Soyadınız</label>
                            <input type="text" className="w-full p-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none" placeholder="Adınız" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">E-posta Adresiniz</label>
                            <input type="email" className="w-full p-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none" placeholder="ornek@email.com" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Mesajınız</label>
                            <textarea className="w-full p-3 bg-white border border-gray-300 rounded-lg h-32 resize-none focus:ring-2 focus:ring-red-500 outline-none" placeholder="Mesajınızı buraya yazın..." />
                        </div>
                        <button className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg transition shadow-md">
                            Gönder
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
}
