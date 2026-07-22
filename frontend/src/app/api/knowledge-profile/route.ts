import { NextResponse } from "next/server";
import { createDemoProfile } from "@/lib/academy/thug-coding-example";
import type { DiscoveryInput, KnowledgeProfile } from "@/lib/academy/types";

export const runtime = "nodejs";

const requiredFields: Array<keyof DiscoveryInput> = [
  "organizationName",
  "mission",
  "knowledge",
  "accomplishments",
  "audience",
  "audienceProblems",
  "desiredTransformation",
  "existingResources",
  "constraints",
  "revenueGoal",
];

function isValidInput(value: unknown): value is DiscoveryInput {
  if (!value || typeof value !== "object") return false;
  const input = value as Record<string, unknown>;
  return (
    requiredFields.every(
      (field) => typeof input[field] === "string" && input[field].trim().length > 0,
    ) &&
    Array.isArray(input.businessModels) &&
    input.businessModels.length > 0
  );
}

function extractOutputText(response: unknown): string | null {
  if (!response || typeof response !== "object") return null;
  const payload = response as { output_text?: unknown; output?: unknown };
  if (typeof payload.output_text === "string") return payload.output_text;
  if (!Array.isArray(payload.output)) return null;

  for (const item of payload.output) {
    if (!item || typeof item !== "object") continue;
    const content = (item as { content?: unknown }).content;
    if (!Array.isArray(content)) continue;
    for (const part of content) {
      if (
        part &&
        typeof part === "object" &&
        typeof (part as { text?: unknown }).text === "string"
      ) {
        return (part as { text: string }).text;
      }
    }
  }
  return null;
}

const knowledgeProfileSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "organization",
    "knowledgeMap",
    "audienceProfile",
    "readiness",
    "opportunities",
    "recommendation",
  ],
  properties: {
    organization: {
      type: "object",
      additionalProperties: false,
      required: ["name", "mission", "academyName"],
      properties: {
        name: { type: "string" },
        mission: { type: "string" },
        academyName: { type: "string" },
      },
    },
    knowledgeMap: {
      type: "object",
      additionalProperties: false,
      required: ["primaryDomains", "secondaryDomains", "skills", "distinctiveMethod"],
      properties: {
        primaryDomains: { type: "array", items: { type: "string" } },
        secondaryDomains: { type: "array", items: { type: "string" } },
        skills: { type: "array", items: { type: "string" } },
        distinctiveMethod: { type: "string" },
      },
    },
    audienceProfile: {
      type: "object",
      additionalProperties: false,
      required: ["primaryAudience", "audienceProblems", "desiredTransformation"],
      properties: {
        primaryAudience: { type: "string" },
        audienceProblems: { type: "array", items: { type: "string" } },
        desiredTransformation: { type: "string" },
      },
    },
    readiness: {
      type: "object",
      additionalProperties: false,
      required: ["strengths", "gaps", "overallAssessment"],
      properties: {
        strengths: { type: "array", items: { type: "string" } },
        gaps: { type: "array", items: { type: "string" } },
        overallAssessment: { type: "string" },
      },
    },
    opportunities: {
      type: "array",
      minItems: 3,
      maxItems: 3,
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "id", "name", "type", "description", "targetCustomer", "primaryOffer",
          "revenueStreams", "scores", "rationale"
        ],
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          type: { type: "string" },
          description: { type: "string" },
          targetCustomer: { type: "string" },
          primaryOffer: { type: "string" },
          revenueStreams: { type: "array", items: { type: "string" } },
          scores: {
            type: "object",
            additionalProperties: false,
            required: [
              "knowledgeFit", "speedToLaunch", "revenuePotential",
              "recurringRevenuePotential", "differentiation",
              "operationalComplexity", "risk"
            ],
            properties: {
              knowledgeFit: { type: "number" },
              speedToLaunch: { type: "number" },
              revenuePotential: { type: "number" },
              recurringRevenuePotential: { type: "number" },
              differentiation: { type: "number" },
              operationalComplexity: { type: "number" },
              risk: { type: "number" },
            },
          },
          rationale: { type: "string" },
        },
      },
    },
    recommendation: {
      type: "object",
      additionalProperties: false,
      required: ["opportunityId", "reason", "nextStep"],
      properties: {
        opportunityId: { type: "string" },
        reason: { type: "string" },
        nextStep: { type: "string" },
      },
    },
  },
};

export async function POST(request: Request) {
  try {
    const input = await request.json();
    if (!isValidInput(input)) {
      return NextResponse.json(
        { error: "Complete every required discovery field before generating a profile." },
        { status: 400 },
      );
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ profile: createDemoProfile(input), mode: "demo" });
    }

    const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || "gpt-5-mini",
        store: false,
        instructions:
          "You are the Knowledge Engine for BUILD. DO. HAVE.™. Analyze the client's actual knowledge and goals. Be practical, specific, security-conscious, and commercially realistic. Do not promise guaranteed revenue. Return exactly three ranked knowledge-business opportunities. The client decides; you recommend.",
        input: JSON.stringify(input),
        text: {
          format: {
            type: "json_schema",
            name: "knowledge_profile",
            strict: true,
            schema: knowledgeProfileSchema,
          },
        },
      }),
    });

    if (!response.ok) {
      const message = await response.text();
      console.error("OpenAI response error:", response.status, message);
      return NextResponse.json(
        { error: "The Knowledge Engine could not complete this analysis." },
        { status: 502 },
      );
    }

    const payload = await response.json();
    const outputText = extractOutputText(payload);
    if (!outputText) {
      return NextResponse.json(
        { error: "The Knowledge Engine returned an empty result." },
        { status: 502 },
      );
    }

    const profile = JSON.parse(outputText) as KnowledgeProfile;
    return NextResponse.json({ profile, mode: "live" });
  } catch (error) {
    console.error("Knowledge profile route error:", error);
    return NextResponse.json(
      { error: "An unexpected error occurred while building the profile." },
      { status: 500 },
    );
  }
}
