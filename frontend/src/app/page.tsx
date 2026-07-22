import Link from "next/link";
import styles from "./page.module.css";
import SiteFooter from "@/components/layout/SiteFooter";

const process = [
  ["01", "Create your workspace", "Name the business or idea you want to build."],
  ["02", "Build your Knowledge Foundation™", "Explain your expertise first, then add the material you have already created."],
  ["03", "Generate your strategy", "The Knowledge Engine™ organizes your expertise into a Knowledge Profile™, Opportunity Map™, and recommended direction."],
  ["04", "Build your company", "Create the blueprint, products, operations, launch strategy, and revenue system inside your recommended Builder™."],
];

const safeguards = [
  ["Encrypted transfer", "Source material travels through HTTPS/TLS."],
  ["Malware screening", "Every uploaded file is quarantined and screened before processing."],
  ["Tenant isolation", "Each organization remains separated from every other workspace."],
  ["Human approval", "The engine organizes the client’s knowledge. The client controls every decision."],
];

export default function HomePage() {
  return (
    <main className={styles.page}>
      <div className={styles.shell}>
        <header className={styles.header}>
          <Link href="/" className={styles.brand}>
            <strong>BUILD. DO. HAVE.<sup>™</sup></strong>
            <span>KNOWLEDGE BUSINESS CREATION SYSTEM</span>
          </Link>
          <nav aria-label="Primary navigation">
            <Link href="#platform">Platform</Link>
            <Link href="#process">Process</Link>
            <Link href="#security">Security</Link>
          </nav>
          <Link href="/build" className={styles.headerAction}>Enter the Studio <span>↗</span></Link>
        </header>

        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <div className={styles.kicker}><span>Knowledge into ownership</span><span>Est. 2026</span></div>
            <h1><span>BUILD.</span><span>DO.</span><span>HAVE.</span></h1>
            <div className={styles.heroBottom}>
              <p>Turn what you know into something you own.</p>
              <Link href="/build" className={styles.primaryAction}>Start building <span>→</span></Link>
            </div>
          </div>

          <aside className={styles.productPreview} aria-label="Product preview">
            <div className={styles.previewHeader}>
              <div><small>WORKSPACE 001</small><strong>Thug Coding® Academy</strong></div>
              <span className={styles.secure}>● Secure session</span>
            </div>
            <div className={styles.previewStage}><span>01</span><div><small>CREATE WORKSPACE</small><strong>Business identity established</strong></div><b>✓</b></div>
            <div className={styles.previewStage}><span>02</span><div><small>KNOWLEDGE INTAKE</small><strong>Discovery + source material</strong></div><b>✓</b></div>
            <div className={`${styles.previewStage} ${styles.active}`}><span>03</span><div><small>KNOWLEDGE ENGINE™</small><strong>Mapping viable opportunities</strong></div><b>78%</b></div>
            <div className={styles.progress}><i /></div>
            <div className={styles.outputCard}>
              <small>RECOMMENDED DIRECTION</small>
              <h2>Academy Builder™</h2>
              <p>Educational expertise, curriculum assets, and recurring membership potential are a strong fit.</p>
              <div><span>Blueprint</span><span>Programs</span><span>Curriculum</span><span>Revenue</span></div>
            </div>
            <footer>Powered by the Knowledge Engine™</footer>
          </aside>
        </section>

        <section id="platform" className={styles.premise}>
          <span>001 / THE PLATFORM</span>
          <h2>One secure workspace for turning expertise into an operating business.</h2>
          <p>BUILD. DO. HAVE.™ combines guided discovery, secure source intake, structured analysis, and specialized Builder™ workflows without replacing the client’s judgment.</p>
        </section>

        <section id="process" className={styles.processSection}>
          <div className={styles.sectionHeading}><span>002 / HOW IT WORKS</span><h2>FROM KNOWLEDGE<br/>TO OWNERSHIP.</h2></div>
          <div className={styles.processGrid}>
            {process.map(([number, title, description]) => (
              <article key={number}><span>{number}</span><h3>{title}</h3><p>{description}</p></article>
            ))}
          </div>
        </section>

        <section id="security" className={styles.securitySection}>
          <div className={styles.sectionHeading}><span>003 / SECURITY BY DESIGN</span><h2>PRIVATE INPUT.<br/>CONTROLLED OUTPUT.</h2></div>
          <div className={styles.securityGrid}>
            {safeguards.map(([title, description]) => <article key={title}><strong>{title}</strong><p>{description}</p></article>)}
          </div>
        </section>

        <section className={styles.exampleSection}>
          <div><span>004 / EXAMPLE OUTPUT</span><h2>A business direction you can inspect before you build.</h2></div>
          <div className={styles.exampleCard}>
            <small>KNOWLEDGE ENGINE™ RECOMMENDATION</small>
            <h3>Academy Builder™</h3>
            <p>Your experience is educational. You already have curriculum-ready material. Certification, membership, and supervised client services create multiple revenue paths.</p>
            <ul><li>Academy Blueprint™</li><li>Program architecture</li><li>Curriculum system</li><li>Launch and revenue plan</li></ul>
          </div>
        </section>

        <section className={styles.finalCta}>
          <span>READY WHEN YOU ARE</span>
          <h2>WHAT WILL<br/>YOU BUILD?</h2>
          <p>Begin with one workspace. Bring an idea, existing material, or both.</p>
          <Link href="/build" className={styles.primaryAction}>Start building <span>→</span></Link>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
