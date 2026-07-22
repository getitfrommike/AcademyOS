import type { DiscoveryInput, KnowledgeProfile } from "./types";

export const thugCodingDiscovery: DiscoveryInput = {
  organizationName: "Thug Coding®",
  mission: "Teach tech in the hood. Make money with tech in the hood.",
  knowledge:
    "Coding, web development, AI tools and automation, cybersecurity, cloud infrastructure, digital entrepreneurship, freelancing, brand building, and technology ownership.",
  accomplishments:
    "Built websites, applications, servers, educational projects, AI systems, a developer portfolio, a technology radio platform, and community-focused technology brands.",
  audience:
    "Underserved aspiring developers, young adults, entrepreneurs, small-business owners, and community organizations.",
  audienceProblems:
    "Limited access to practical technology education, uncertainty about what to learn, difficulty turning technical skills into income, and lack of trusted mentorship.",
  desiredTransformation:
    "Move learners from technology consumers to confident builders and owners who can create, secure, launch, and monetize real digital products.",
  businessModels: ["Academy", "Certification", "Membership", "Business services"],
  existingResources:
    "Brand identity, website concepts, coding tutorials, project documentation, cybersecurity checklists, infrastructure notes, course ideas, portfolio projects, and community mission.",
  constraints:
    "Begin with a focused minimum viable academy, keep operating costs controlled, use a small founding team, and launch curriculum in stages.",
  revenueGoal:
    "Create tuition revenue first, then add recurring membership, certification, sponsorship, and supervised client-service revenue.",
};

export function createDemoProfile(input: DiscoveryInput): KnowledgeProfile {
  return {
    organization: {
      name: input.organizationName,
      mission: input.mission,
      academyName: "Thug Coding Academy™",
    },
    knowledgeMap: {
      primaryDomains: [
        "Web development",
        "AI integration",
        "Cybersecurity",
        "Digital entrepreneurship",
      ],
      secondaryDomains: [
        "Cloud infrastructure",
        "Freelancing",
        "Brand building",
        "Community education",
      ],
      skills: [
        "Build and deploy websites",
        "Design practical AI workflows",
        "Apply security-by-design practices",
        "Package technical skills into client offers",
      ],
      distinctiveMethod:
        "Learn by building, securing, launching, and presenting real revenue-generating technology assets.",
    },
    audienceProfile: {
      primaryAudience: input.audience,
      audienceProblems: input.audienceProblems
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      desiredTransformation: input.desiredTransformation,
    },
    readiness: {
      strengths: [
        "Clear mission and distinctive voice",
        "Broad real-world technical experience",
        "Strong project-based learning philosophy",
        "Multiple future revenue paths",
      ],
      gaps: [
        "Validate the first student segment",
        "Define measurable certification standards",
        "Select the minimum launch curriculum",
      ],
      overallAssessment:
        "Strong foundation for a focused academy. Begin with one flagship transformation and prove outcomes before expanding the catalog.",
    },
    opportunities: [
      {
        id: "flagship-academy",
        name: "Thug Coding Academy™",
        type: "Academy",
        description:
          "A structured technology and entrepreneurship academy where students build production-ready digital businesses.",
        targetCustomer:
          "Aspiring developers and entrepreneurs who need a practical path from learning to ownership.",
        primaryOffer: "Build Your First Technology Business — 12-week flagship program",
        revenueStreams: ["Tuition", "Membership", "Certification", "Sponsorship"],
        scores: {
          knowledgeFit: 96,
          speedToLaunch: 78,
          revenuePotential: 91,
          recurringRevenuePotential: 86,
          differentiation: 95,
          operationalComplexity: 68,
          risk: 35,
        },
        rationale:
          "This best combines the brand mission, technical range, teaching philosophy, and long-term ownership model.",
      },
      {
        id: "web-certification",
        name: "Community Web Developer Certification",
        type: "Certification",
        description:
          "A competency-based program centered on building and securing a production-ready small-business website.",
        targetCustomer:
          "Entry-level builders seeking a concrete portfolio credential and employable proof of work.",
        primaryOffer: "Six-week certification sprint with a reviewed capstone",
        revenueStreams: ["Enrollment", "Assessment fees", "Employer partnerships"],
        scores: {
          knowledgeFit: 92,
          speedToLaunch: 90,
          revenuePotential: 76,
          recurringRevenuePotential: 62,
          differentiation: 88,
          operationalComplexity: 52,
          risk: 28,
        },
        rationale:
          "Fastest path to a credible paid offer with a clear, demonstrable student outcome.",
      },
      {
        id: "builder-network",
        name: "Thug Coding Builder Network",
        type: "Membership",
        description:
          "An ongoing builder community with workshops, project reviews, templates, opportunities, and business guidance.",
        targetCustomer:
          "Learners and early-stage freelancers who need continued accountability and access after a course.",
        primaryOffer: "Monthly membership with live build sessions and opportunity briefings",
        revenueStreams: ["Monthly membership", "Premium workshops", "Partner offers"],
        scores: {
          knowledgeFit: 88,
          speedToLaunch: 84,
          revenuePotential: 79,
          recurringRevenuePotential: 96,
          differentiation: 84,
          operationalComplexity: 61,
          risk: 31,
        },
        rationale:
          "Creates recurring revenue and a long-term community, but works best after the flagship offer establishes trust.",
      },
    ],
    recommendation: {
      opportunityId: "flagship-academy",
      reason:
        "Launch the academy as the master brand, begin with one flagship program, and use the certification and membership as the next layers.",
      nextStep:
        "Approve the recommended direction, then generate the Academy Blueprint and first flagship-program architecture.",
    },
  };
}
