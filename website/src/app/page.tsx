import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Screenshots from "@/components/Screenshots";
import SystemRequirements from "@/components/SystemRequirements";
import Download from "@/components/Download";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Screenshots />
      <SystemRequirements />
      <Download />
      <FAQ />
      <Footer />
    </main>
  );
}
