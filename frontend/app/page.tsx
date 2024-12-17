"use client";

import Search from "@/components/Search";
import { motion } from "framer-motion";
import Script from "next/script";

export default function Home() {
  return (
    <div className="bg-transparent text-default font-sans min-h-screen overflow-hidden relative py-8">
      <Script src="https://kit.fontawesome.com/3d72938be8.js" />

      <motion.header
        className="text-2xl font-bold ml-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1}}
        transition={{ duration: 0.5 }}
      >
        <h1>
      
          <i className="fa-solid fa-compass text-[#56875a] mr-2 fa-xl"></i>
          Compass
        </h1>
      </motion.header>
      <Search />
    </div>
  );
}
