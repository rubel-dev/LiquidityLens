"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const links = [
  { href: "/agent", label: "Agent View" },
  { href: "/ops", label: "Operations" },
  { href: "/cases", label: "Cases" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-3">
          <span className="text-blue-400 font-bold text-lg">LiquidityAI</span>
          <span className="text-gray-600 text-xs hidden sm:block">bKash · Nagad · Rocket</span>
        </div>
        <nav className="flex gap-1">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={clsx(
                "px-3 py-1.5 rounded text-sm font-medium transition-colors",
                path.startsWith(l.href)
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              )}
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
