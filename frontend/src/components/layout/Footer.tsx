import Link from "next/link";
import styles from "./footer.module.css";

export default function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={styles.brandBlock}>
        <strong>BUILD. DO. HAVE.<sup>™</sup></strong>
        <p>Turn what you know into something you own.</p>
      </div>
      <nav aria-label="Footer navigation">
        <Link href="/#platform">Platform</Link>
        <Link href="/#process">Process</Link>
        <Link href="/#security">Security</Link>
        <Link href="/build">Enter the Studio</Link>
      </nav>
      <div className={styles.meta}>
        <span>Powered by the Knowledge Engine™</span>
        <span>Secure by design</span>
        <span>© 2026 BUILD. DO. HAVE.™</span>
      </div>
    </footer>
  );
}
