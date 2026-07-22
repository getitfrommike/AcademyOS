"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import { thugCodingDiscovery } from "@/lib/academy/thug-coding-example";
import type { DiscoveryInput, KnowledgeProfile, Opportunity } from "@/lib/academy/types";
import styles from "./academy.module.css";

const modelOptions = [
  "Academy",
  "Course",
  "Certification",
  "Membership",
  "Coaching",
  "Consulting",
  "Licensing",
  "Business services",
];

const fields: Array<{
  key: keyof Omit<DiscoveryInput, "businessModels">;
  label: string;
  helper: string;
  rows?: number;
}> = [
  { key: "organizationName", label: "Organization", helper: "What is the current brand or working company name?" },
  { key: "mission", label: "Mission", helper: "What change are you committed to creating?", rows: 3 },
  { key: "knowledge", label: "What do you know?", helper: "List your strongest subjects, methods, skills, and experience.", rows: 5 },
  { key: "accomplishments", label: "What have you built or accomplished?", helper: "Include projects, results, systems, products, teaching, and client work.", rows: 5 },
  { key: "audience", label: "Who do you want to serve?", helper: "Describe the people, organizations, or communities you understand best.", rows: 4 },
  { key: "audienceProblems", label: "What problems can you help them solve?", helper: "Name the practical barriers, frustrations, and unmet needs.", rows: 4 },
  { key: "desiredTransformation", label: "What transformation should they achieve?", helper: "Describe the before-and-after result your academy should produce.", rows: 4 },
  { key: "existingResources", label: "What resources already exist?", helper: "Notes, tutorials, websites, videos, checklists, projects, testimonials, or brand assets.", rows: 4 },
  { key: "constraints", label: "What constraints must the plan respect?", helper: "Budget, time, team, launch date, technology, or operational limits.", rows: 4 },
  { key: "revenueGoal", label: "What revenue model interests you?", helper: "Explain how you would like the knowledge company to earn money.", rows: 4 },
];

function ScoreBar({ label, value, inverse = false }: { label: string; value: number; inverse?: boolean }) {
  const adjusted = inverse ? 100 - value : value;
  return (
    <div className={styles.scoreRow}>
      <span>{label}</span>
      <div className={styles.scoreTrack}><span style={{ width: `${adjusted}%` }} /></div>
      <strong>{value}</strong>
    </div>
  );
}

function OpportunityCard({ opportunity, recommended, selected, onSelect }: {
  opportunity: Opportunity;
  recommended: boolean;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <article className={`${styles.opportunityCard} ${selected ? styles.selectedCard : ""}`}>
      <div className={styles.cardTopline}>
        <span>{opportunity.type}</span>
        {recommended && <strong>Recommended</strong>}
      </div>
      <h3>{opportunity.name}</h3>
      <p>{opportunity.description}</p>
      <div className={styles.offerBlock}>
        <span>Primary offer</span>
        <strong>{opportunity.primaryOffer}</strong>
      </div>
      <div className={styles.scoreList}>
        <ScoreBar label="Knowledge fit" value={opportunity.scores.knowledgeFit} />
        <ScoreBar label="Launch speed" value={opportunity.scores.speedToLaunch} />
        <ScoreBar label="Revenue" value={opportunity.scores.revenuePotential} />
        <ScoreBar label="Recurring" value={opportunity.scores.recurringRevenuePotential} />
        <ScoreBar label="Complexity" value={opportunity.scores.operationalComplexity} inverse />
      </div>
      <p className={styles.rationale}>{opportunity.rationale}</p>
      <button type="button" onClick={onSelect} className={styles.selectButton}>
        {selected ? "Direction selected" : "Select this direction"}
      </button>
    </article>
  );
}

export default function AcademyPage() {
  const [input, setInput] = useState<DiscoveryInput>(thugCodingDiscovery);
  const [profile, setProfile] = useState<KnowledgeProfile | null>(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState<string>("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [mode, setMode] = useState<"demo" | "live" | "">("");

  const completedFields = useMemo(() => {
    const textFields = fields.filter(({ key }) => input[key].trim().length > 0).length;
    return textFields + (input.businessModels.length ? 1 : 0);
  }, [input]);

  const progress = Math.round((completedFields / (fields.length + 1)) * 100);

  function updateField(key: keyof Omit<DiscoveryInput, "businessModels">, value: string) {
    setInput((current) => ({ ...current, [key]: value }));
  }

  function toggleModel(model: string) {
    setInput((current) => ({
      ...current,
      businessModels: current.businessModels.includes(model)
        ? current.businessModels.filter((item) => item !== model)
        : [...current.businessModels, model],
    }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setMessage("");
    setProfile(null);
    setSelectedOpportunity("");

    try {
      const response = await fetch("/api/knowledge-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Unable to generate profile.");
      setProfile(payload.profile);
      setMode(payload.mode);
      setSelectedOpportunity(payload.profile.recommendation.opportunityId);
      setStatus("success");
      requestAnimationFrame(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }));
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Unable to generate profile.");
    }
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href="/" className={styles.brand}>BUILD. DO. HAVE.<sup>™</sup></Link>
        <div className={styles.headerCenter}>Discovery Intake™ <span>→</span> Knowledge Profile</div>
        <span className={styles.secure}>Secure session</span>
      </header>

      <section className={styles.intro}>
        <div>
          <span className={styles.kicker}>Knowledge company example 001</span>
          <h1>Build the Thug Coding® academy.</h1>
        </div>
        <p>
          Refine the client discovery record, then send it through the Knowledge Engine™ to produce a structured Knowledge Profile and Opportunity Map™.
        </p>
      </section>

      <div className={styles.workspace}>
        <aside className={styles.rail}>
          <span className={styles.railLabel}>Build sequence</span>
          {[
            ["01", "Discovery Intake", "active"],
            ["02", "Knowledge Profile", profile ? "complete" : ""],
            ["03", "Opportunity Map", profile ? "complete" : ""],
            ["04", "Direction Approval", selectedOpportunity ? "active" : ""],
            ["05", "Academy Blueprint", "locked"],
          ].map(([number, label, state]) => (
            <div key={number} className={`${styles.railStep} ${state ? styles[state] : ""}`}>
              <span>{number}</span><strong>{label}</strong>
            </div>
          ))}
          <div className={styles.progressCard}>
            <div><span>Intake completion</span><strong>{progress}%</strong></div>
            <div className={styles.progressTrack}><span style={{ width: `${progress}%` }} /></div>
          </div>
        </aside>

        <form className={styles.form} onSubmit={submit}>
          <div className={styles.formHeader}>
            <span>Secure Knowledge Intake™</span>
            <strong>Thug Coding® client record</strong>
            <p>Everything below remains editable. The AI should organize the client’s knowledge—not replace the client’s judgment.</p>
          </div>

          {fields.map(({ key, label, helper, rows = 1 }, index) => (
            <label className={styles.field} key={key}>
              <span className={styles.fieldNumber}>{String(index + 1).padStart(2, "0")}</span>
              <span className={styles.fieldText}><strong>{label}</strong><small>{helper}</small></span>
              {rows > 1 ? (
                <textarea value={input[key]} rows={rows} onChange={(event) => updateField(key, event.target.value)} />
              ) : (
                <input value={input[key]} onChange={(event) => updateField(key, event.target.value)} />
              )}
            </label>
          ))}

          <fieldset className={styles.modelField}>
            <legend><strong>What do you want to build?</strong><small>Select every business model worth evaluating.</small></legend>
            <div className={styles.modelGrid}>
              {modelOptions.map((model) => (
                <button key={model} type="button" onClick={() => toggleModel(model)} className={input.businessModels.includes(model) ? styles.modelSelected : ""}>
                  <span>{input.businessModels.includes(model) ? "✓" : "+"}</span>{model}
                </button>
              ))}
            </div>
          </fieldset>

          <div className={styles.submitPanel}>
            <div><span>Next operation</span><strong>Analyze knowledge and map viable academy opportunities.</strong></div>
            <button type="submit" disabled={status === "loading"}>{status === "loading" ? "Knowledge Engine working…" : "Build Knowledge Profile →"}</button>
          </div>
          {status === "error" && <p className={styles.error}>{message}</p>}
        </form>
      </div>

      {profile && (
        <section id="results" className={styles.results}>
          <div className={styles.resultsHeader}>
            <div><span className={styles.kicker}>Knowledge Engine™ output</span><h2>{profile.organization.academyName}</h2></div>
            <span className={styles.modeBadge}>{mode === "live" ? "Live AI analysis" : "Demo analysis — add API key for live AI"}</span>
          </div>

          <div className={styles.profileGrid}>
            <article className={styles.profileCard}><span>Knowledge map</span><h3>Primary domains</h3><div className={styles.tagList}>{profile.knowledgeMap.primaryDomains.map((item) => <strong key={item}>{item}</strong>)}</div><p>{profile.knowledgeMap.distinctiveMethod}</p></article>
            <article className={styles.profileCard}><span>Audience profile</span><h3>Who this serves</h3><p>{profile.audienceProfile.primaryAudience}</p><strong className={styles.transformation}>{profile.audienceProfile.desiredTransformation}</strong></article>
            <article className={styles.profileCard}><span>Readiness</span><h3>Foundation assessment</h3><p>{profile.readiness.overallAssessment}</p><ul>{profile.readiness.gaps.map((gap) => <li key={gap}>{gap}</li>)}</ul></article>
          </div>

          <div className={styles.mapHeading}><span>Opportunity Map™</span><h2>Three viable directions. One recommended starting point.</h2></div>
          <div className={styles.opportunityGrid}>
            {profile.opportunities.map((opportunity) => (
              <OpportunityCard key={opportunity.id} opportunity={opportunity} recommended={profile.recommendation.opportunityId === opportunity.id} selected={selectedOpportunity === opportunity.id} onSelect={() => setSelectedOpportunity(opportunity.id)} />
            ))}
          </div>

          <div className={styles.approvalPanel}>
            <div><span>Direction confirmation</span><h3>{profile.opportunities.find((item) => item.id === selectedOpportunity)?.name}</h3><p>{profile.recommendation.nextStep}</p></div>
            <button type="button">Approve and build blueprint →</button>
          </div>
        </section>
      )}
    </main>
  );
}
