import Nav from "../components/Nav";
import Hero from "../components/Hero";
import Problem from "../components/Problem";
import Solution from "../components/Solution";
import Features from "../components/Features";

export default function Home() {
  return (
    <main className="tracking-wide w-full flex flex-col items-center">
      <div className="relative">
        <Nav />
      </div>

      <Hero />
      <Problem />
      <Solution />
      <Features />
    </main>
  );
}
