"use client";


import Search from "@/components/Search";
import Script from "next/script";

export default function Home() {
  return (
    <div className="bg-transparent text-default font-sans min-h-screen overflow-hidden relative py-8">
      <Script src="https://kit.fontawesome.com/3d72938be8.js" />
      
      
      <Search />
    </div>
  );
}
