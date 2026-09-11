import streamlit as st

from Agents.Profile_Analyzer import ProfileAnalyzer
from Agents.Activity_Analyzer import ActivityAnalyzer
from Agents.Identity_OSINT import IdentityOSINTAgent
from Agents.Evidence_Verifier import EvidenceVerifier
from Agents.Report_Generator import ReportGenerator


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="X Account Investigator",
    page_icon="🔎",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🔎 X Account Investigator")

st.write(
    "AI-powered investigation of publicly available "
    "X account information."
)

st.divider()


# =========================================================
# INPUT
# =========================================================

username = st.text_input(
    "Enter X Username",
    placeholder="e.g. Cristiano",
)

investigate = st.button(
    "🔍 Investigate Account",
    type="primary"
)


# =========================================================
# INVESTIGATION
# =========================================================

if investigate:

    if not username.strip():

        st.warning("Please enter an X username.")

    else:

        username = username.strip().lstrip("@")

        # -------------------------------------------------
        # AGENT 1
        # -------------------------------------------------

        with st.spinner("Running Profile Analyzer..."):

            profile_agent = ProfileAnalyzer()

            profile_result = profile_agent.analyse_profile(
                username
            )

        # -------------------------------------------------
        # AGENT 2
        # -------------------------------------------------

        with st.spinner("Running Activity Analyzer..."):

            activity_agent = ActivityAnalyzer()

            activity_result = activity_agent.analyse_activity(
                username
            )

        # -------------------------------------------------
        # AGENT 3
        # -------------------------------------------------

        with st.spinner("Running Identity OSINT Agent..."):

            identity_agent = IdentityOSINTAgent()

            identity_result = identity_agent.analyse_identity(
                username
            )

        # -------------------------------------------------
        # AGENT 4
        # -------------------------------------------------

        with st.spinner("Verifying evidence..."):

            verifier = EvidenceVerifier()

            verification_result = verifier.verify(
                profile_result,
                activity_result,
                identity_result
            )

        # -------------------------------------------------
        # AGENT 5
        # -------------------------------------------------

        with st.spinner("Generating investigation report..."):

            report_generator = ReportGenerator()

            report_path = report_generator.generate_report(
                username=username,
                profile_result=profile_result,
                activity_result=activity_result,
                identity_result=identity_result,
                verification_result=verification_result
            )

        st.success("Investigation completed successfully.")

        st.divider()

        # =================================================
        # PROFILE
        # =================================================

        st.header("👤 Profile")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Followers",
                profile_result.followers
            )

        with col2:
            st.metric(
                "Following",
                profile_result.following
            )

        with col3:
            st.metric(
                "Posts",
                profile_result.post_count
            )

        with col4:
            st.write("**Account Type**")
            st.write(profile_result.account_type)

        st.write(
            f"**Display Name:** "
            f"{profile_result.display_name}"
        )

        st.write(
            f"**Username:** "
            f"@{profile_result.username}"
        )

        st.write(
            f"**Profile URL:** "
            f"{profile_result.profile_url}"
        )

        st.write(
            f"**Notable Information:** "
            f"{profile_result.notable_information}"
        )

        # =================================================
        # ACTIVITY
        # =================================================

        st.divider()

        st.header("📊 Activity Analysis")

        st.subheader("Recent Activity")

        st.write(
            activity_result.recent_activity_summary
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Primary Topics")

            st.write(
                activity_result.primary_topics
            )

        with col2:

            st.subheader("Common Hashtags")

            st.write(
                activity_result.common_hashtags
            )

        st.subheader("Activity Patterns")

        st.write(
            activity_result.activity_patterns
        )

        st.write(
            f"**Confidence:** "
            f"{activity_result.confidence_level}"
        )

        # =================================================
        # POSTS
        # =================================================

        st.subheader("📝 Recent / Notable Posts")

        if activity_result.notable_posts:

            for post in activity_result.notable_posts:

                st.write(
                    f"• {post}"
                )

        else:

            st.info("No notable posts found.")

        # =================================================
        # IDENTITY
        # =================================================

        st.divider()

        st.header("🕵️ Identity / OSINT")

        st.subheader("Professional Background")

        st.write(
            identity_result.professional_background
        )

        st.subheader("Organizations")

        st.write(
            identity_result.organizations
        )

        # =================================================
        # EVIDENCE
        # =================================================

        st.divider()

        st.header("🔬 Evidence Verification")

        # Confidence
        st.subheader("Confidence Score")

        st.info(
            str(verification_result.confidence_score)
        )

        # Verified findings
        st.subheader("✅ Verified Findings")

        if verification_result.verified_findings:

            for finding in verification_result.verified_findings:

                st.success(finding)

        else:

            st.write("No verified findings.")

        # Conflicts
        st.subheader("⚠️ Conflicting Findings")

        if verification_result.conflicting_findings:

            for conflict in verification_result.conflicting_findings:

                st.warning(conflict)

        else:

            st.success("No conflicts found.")

        # Final assessment
        st.subheader("📋 Final Assessment")

        st.write(
            verification_result.final_assessment
        )

        # =================================================
        # REPORT
        # =================================================

        st.divider()

        st.header("📄 Investigation Report")

        st.success(
            f"Report generated: {report_path}"
        )

        # Read PDF and provide download button

        with open(report_path, "rb") as pdf_file:

            st.download_button(
                label="⬇️ Download Investigation Report",
                data=pdf_file,
                file_name=f"{username}_investigation_report.pdf",
                mime="application/pdf"
            )