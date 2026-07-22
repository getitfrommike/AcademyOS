export type DiscoveryInput = {
  organizationName: string;
  mission: string;
  knowledge: string;
  accomplishments: string;
  audience: string;
  audienceProblems: string;
  desiredTransformation: string;
  businessModels: string[];
  existingResources: string;
  constraints: string;
  revenueGoal: string;
};

export type Opportunity = {
  id: string;
  name: string;
  type: string;
  description: string;
  targetCustomer: string;
  primaryOffer: string;
  revenueStreams: string[];
  scores: {
    knowledgeFit: number;
    speedToLaunch: number;
    revenuePotential: number;
    recurringRevenuePotential: number;
    differentiation: number;
    operationalComplexity: number;
    risk: number;
  };
  rationale: string;
};

export type KnowledgeProfile = {
  organization: {
    name: string;
    mission: string;
    academyName: string;
  };
  knowledgeMap: {
    primaryDomains: string[];
    secondaryDomains: string[];
    skills: string[];
    distinctiveMethod: string;
  };
  audienceProfile: {
    primaryAudience: string;
    audienceProblems: string[];
    desiredTransformation: string;
  };
  readiness: {
    strengths: string[];
    gaps: string[];
    overallAssessment: string;
  };
  opportunities: Opportunity[];
  recommendation: {
    opportunityId: string;
    reason: string;
    nextStep: string;
  };
};
