"use client";

import { useEffect, useState } from "react";
import styles from "./theme-controls.module.css";

type ThemeMode = "light" | "dark";
type FontChoice = "editorial" | "modern" | "classic" | "mono";

const fontMap: Record<FontChoice, string> = {
  editorial: 'Georgia, "Times New Roman", serif',
  modern: 'Arial, Helvetica, sans-serif',
  classic: 'Garamond, Georgia, serif',
  mono: '"Courier New", Courier, monospace',
};

export default function ThemeControls() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<ThemeMode>("light");
  const [accent, setAccent] = useState("#0717ff");
  const [font, setFont] = useState<FontChoice>("editorial");

  useEffect(() => {
    const savedMode = (localStorage.getItem("bdh-theme") as ThemeMode) || "light";
    const savedAccent = localStorage.getItem("bdh-accent") || "#0717ff";
    const savedFont = (localStorage.getItem("bdh-font") as FontChoice) || "editorial";
    setMode(savedMode); setAccent(savedAccent); setFont(savedFont);
    apply(savedMode, savedAccent, savedFont);
  }, []);

  function apply(nextMode: ThemeMode, nextAccent: string, nextFont: FontChoice) {
    document.documentElement.dataset.theme = nextMode;
    document.documentElement.style.setProperty("--accent", nextAccent);
    document.documentElement.style.setProperty("--display-font", fontMap[nextFont]);
    localStorage.setItem("bdh-theme", nextMode);
    localStorage.setItem("bdh-accent", nextAccent);
    localStorage.setItem("bdh-font", nextFont);
  }

  return <div className={styles.wrap}>
    <button className={styles.trigger} onClick={()=>setOpen(!open)} aria-label="Appearance settings">Aa</button>
    {open && <div className={styles.panel}>
      <div className={styles.heading}><strong>Appearance</strong><button onClick={()=>setOpen(false)}>×</button></div>
      <label>Accent color<input type="color" value={accent} onChange={e=>{setAccent(e.target.value); apply(mode,e.target.value,font)}} /></label>
      <label>Display font<select value={font} onChange={e=>{const v=e.target.value as FontChoice; setFont(v); apply(mode,accent,v)}}><option value="editorial">Editorial serif</option><option value="classic">Classic serif</option><option value="modern">Modern sans</option><option value="mono">Monospace</option></select></label>
      <div className={styles.mode}><span>Theme</span><button className={mode==="light"?styles.active:""} onClick={()=>{setMode("light");apply("light",accent,font)}}>Light</button><button className={mode==="dark"?styles.active:""} onClick={()=>{setMode("dark");apply("dark",accent,font)}}>Dark</button></div>
      <small>Saved on this device.</small>
    </div>}
  </div>
}
