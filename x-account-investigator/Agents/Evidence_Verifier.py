from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List

from Agents.BaseAgent import BaseAgent


class VerificationAnalysis(BaseModel):

    verified_findings: List[str]
    conflicting_findings: List[str]
    unsupported_claims: List[str]
    confidence_score: str
    final_assessment: str


class EvidenceVerifier(BaseAgent):

    def __init__(self):
        super().__init__()

        self.verification_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an Evidence Verification Agent.

Your responsibility is to review findings produced by multiple
investigation agents and determine which findings are supported.

Tasks:

1. Identify verified findings.
2. Detect contradictions.
3. Detect unsupported claims.
4. Assess overall confidence.
5. Produce a final assessment.

Rules:

1. Use ONLY the provided agent outputs.
2. Do NOT invent evidence.
3. Do NOT add new information.
4. If two agents support the same finding, treat it as stronger evidence.
5. If a finding appears only once and lacks support, mark it as potentially unsupported.
6. Confidence must be High, Medium, or Low.

Return structured output only.
"""
                ),
                (
                    "human",
                    """
Profile Agent Output:

{profile_output}


Activity Agent Output:

{activity_output}


Identity Agent Output:

{identity_output}


Perform verification and assessment.
"""
                )
            ]
        )

        self.structured_llm = self.llm.with_structured_output(
            VerificationAnalysis
        )

    def verify(
        self,
        profile_output,
        activity_output,
        identity_output
    ):

        prompt = self.verification_prompt.invoke(
            {
                "profile_output": profile_output,
                "activity_output": activity_output,
                "identity_output": identity_output
            }
        )

        result = self.structured_llm.invoke(prompt)

        return result


if __name__ == "__main__":

    profile_output = """
Username: Cristiano
Display Name: Cristiano Ronaldo
Account Type: Public Figure
Followers: 114000000
"""

    activity_output = """
Primary Topics:
- Football
- Sports

Recent Activity:
- Football related posts
"""

    identity_output = """
Professional Background:
- Professional Football Player

Organizations:
- Al Nassr
"""

    verifier = EvidenceVerifier()

    result = verifier.verify(
        profile_output,
        activity_output,
        identity_output
    )

    print("\n")
    print("          EVIDENCE VERIFICATION REPORT")

    print("\nVerified Findings")
    print("-" * 60)

    if result.verified_findings:
        for item in result.verified_findings:
            print(f"• {item}")
    else:
        print("No verified findings.")

    print("\nConflicting Findings")
    print("-" * 60)

    if result.conflicting_findings:
        for item in result.conflicting_findings:
            print(f"• {item}")
    else:
        print("No conflicts found.")

    print("\nUnsupported Claims")
    print("-" * 60)

    if result.unsupported_claims:
        for item in result.unsupported_claims:
            print(f"• {item}")
    else:
        print("No unsupported claims.")

    print("\nConfidence Score")
    print("-" * 60)
    print(result.confidence_score)

    print("\nFinal Assessment")
    print("-" * 60)
    print(result.final_assessment)