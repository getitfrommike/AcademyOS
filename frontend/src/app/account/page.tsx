"use client";
import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import styles from "./account.module.css";
import SiteFooter from "@/components/layout/Footer";
import { apiPost } from "@/lib/api";

function AccountPageContent(){
  const router=useRouter(); const params=useSearchParams();
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [displayName,setDisplayName]=useState("");
  const [workspace,setWorkspace]=useState("Your workspace"); const [organization,setOrganization]=useState("");
  const [error,setError]=useState(""); const [busy,setBusy]=useState(false);
  useEffect(()=>{const saved=localStorage.getItem("bdh-workspace");if(saved){const d=JSON.parse(saved);setWorkspace(d.workspace||"Your workspace");setOrganization(d.organization||"")}},[]);
  async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError("");try{const data=await apiPost<{user:{email:string}}>("/api/auth/signup/",{email,password,display_name:displayName,workspace_name:workspace,organization_name:organization});localStorage.setItem("bdh-auth",JSON.stringify(data.user));router.push(params.get("return")||"/build")}catch(err:any){const messages=Object.values(err||{}).flat().join(" ");setError(messages||"We could not secure your workspace.")}finally{setBusy(false)}}
  return <main className={styles.page}><header><Link href="/">BUILD. DO. HAVE.<sup>™</sup></Link><span>Secure your workspace</span></header><section><p>WORKSPACE SECURITY / 001</p><h1>Secure Your Workspace.</h1><p className={styles.lead}>You have started building <strong>{workspace}</strong>. Create your account before source files are stored, scanned, or processed.</p><form onSubmit={submit}><label>Your name <small>Optional</small><input value={displayName} onChange={e=>setDisplayName(e.target.value)}/></label><label>Email address<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></label><label>Password<input type="password" minLength={12} value={password} onChange={e=>setPassword(e.target.value)} required /></label>{error&&<p role="alert">{error}</p>}<button disabled={busy}>{busy?"Securing workspace…":"Secure my workspace →"}</button></form><small>Account creation saves your workspace, creates its owner organization, and starts an authenticated Django session.</small></section><SiteFooter /></main>}

export default function AccountPage(){return <Suspense fallback={<main style={{padding:40}}>Loading secure workspace…</main>}><AccountPageContent /></Suspense>}
