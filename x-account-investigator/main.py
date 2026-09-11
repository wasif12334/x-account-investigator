from Agents.Profile_Analyzer import ProfileAnalyzer
from Agents.Activity_Analyzer import ActivityAnalyzer
from Agents.Identity_OSINT import IdentityOSINTAgent
from Agents.Evidence_Verifier import EvidenceVerifier
from Agents.Report_Generator import ReportGenerator


def main():

    username = input("Enter X Username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    print("\n" + "=" * 70)
    print("X ACCOUNT INVESTIGATION SYSTEM")
    print("=" * 70)

    # ==================================================
    # AGENT 1 - PROFILE ANALYZER
    # ==================================================

    print("\n[1/5] Running Profile Analyzer...")

    profile_agent = ProfileAnalyzer()

    profile_result = profile_agent.analyse_profile(username)

    print("✓ Profile analysis completed.")

    # ==================================================
    # AGENT 2 - ACTIVITY ANALYZER
    # ==================================================

    print("\n[2/5] Running Activity Analyzer...")

    activity_agent = ActivityAnalyzer()

    activity_result = activity_agent.analyse_activity(username)

    print("✓ Activity analysis completed.")

    # ==================================================
    # AGENT 3 - IDENTITY OSINT
    # ==================================================

    print("\n[3/5] Running Identity OSINT Agent...")

    identity_agent = IdentityOSINTAgent()

    identity_result = identity_agent.analyse_identity(username)

    print("✓ Identity investigation completed.")

    # ==================================================
    # AGENT 4 - EVIDENCE VERIFIER
    # ==================================================

    print("\n[4/5] Running Evidence Verifier...")

    verifier = EvidenceVerifier()

    verification_result = verifier.verify(
        profile_result,
        activity_result,
        identity_result
    )

    print("✓ Evidence verification completed.")

    # ==================================================
    # AGENT 5 - REPORT GENERATOR
    # ==================================================

    print("\n[5/5] Generating Investigation Report...")

    report_generator = ReportGenerator()

    report_path = report_generator.generate_report(
        username=username,
        profile_result=profile_result,
        activity_result=activity_result,
        identity_result=identity_result,
        verification_result=verification_result
    )

    print("✓ Investigation report generated.")

    # ==================================================
    # FINAL TERMINAL SUMMARY
    # ==================================================

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)

    print(f"\nUsername: @{username}")

    print(
        f"Confidence Score: "
        f"{verification_result.confidence_score}"
    )

    print("\nFinal Assessment:")
    print(verification_result.final_assessment)

    print("\nReport:")
    print(report_path)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()