import streamlit as st
from tools.primary_key_validator import show_primary_key_validator

# Page configuration
st.set_page_config(
    page_title="Excel Toolkit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-description {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .tool-description h3 {
        margin-top: 0;
        color: #1f77b4;
    }
    .tool-description p {
        margin-bottom: 0;
        opacity: 0.8;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    # Sidebar navigation
    st.sidebar.title("🛠️ Excel Toolkit")
    st.sidebar.markdown("---")

    # Tool selection
    tool_options = [
        "🏠 Home",
        "🔑 Primary Key Validator",
        "🔗 Foreign Key Validator",
        "🔍 Lookup & Update",
        "📊 Data Merger",
        "⚖️ Sheet Comparer",
        "🔄 Duplicate Detector",
    ]

    selected_tool = st.sidebar.selectbox("Select Tool:", tool_options)

    # Main content area
    if selected_tool == "🏠 Home":
        show_home_page()
    elif selected_tool == "🔑 Primary Key Validator":
        show_primary_key_validator()
    elif selected_tool == "🔗 Foreign Key Validator":
        show_foreign_key_validator()
    elif selected_tool == "🔍 Lookup & Update":
        show_lookup_update()
    elif selected_tool == "📊 Data Merger":
        show_data_merger()
    elif selected_tool == "⚖️ Sheet Comparer":
        show_sheet_comparer()
    elif selected_tool == "🔄 Duplicate Detector":
        show_duplicate_detector()


def show_home_page():
    st.markdown(
        '<h1 class="main-header">📊 Excel Toolkit Suite</h1>', unsafe_allow_html=True
    )

    st.markdown(
        """
    Welcome to your comprehensive Excel automation toolkit! This suite provides powerful tools 
    to streamline your Excel workflow and eliminate repetitive manual tasks.
    """
    )

    # Tool overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="tool-description">
        <h3>🔑 Primary Key Validator</h3>
        <p>Validate uniqueness of primary keys across sheets and workbooks. 
        Identify duplicate records and maintain data integrity.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="tool-description">
        <h3>📊 Data Merger</h3>
        <p>Combine data from multiple Excel files with intelligent conflict resolution 
        and customizable merge strategies.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="tool-description">
        <h3>🔄 Duplicate Detector</h3>
        <p>Find and highlight duplicate records across your datasets with 
        flexible matching criteria.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="tool-description">
        <h3>🔗 Foreign Key Validator</h3>
        <p>Ensure data integrity by validating foreign key relationships across
        different Excel files. Identify orphaned records and maintain relational integrity.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="tool-description">
        <h3>🔍 Lookup & Update</h3>
        <p>Perform VLOOKUP-style operations between workbooks. Update existing 
        data with new information seamlessly.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="tool-description">
        <h3>⚖️ Sheet Comparer</h3>
        <p>Compare data between different sheets or workbooks. Identify 
        differences and generate detailed comparison reports.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.info(
        "💡 **Getting Started**: Select a tool from the sidebar to begin. Each tool includes step-by-step guidance and examples."
    )


def show_primary_key_validator():
    """Function now handled by the actual tool"""
    from tools.primary_key_validator import show_primary_key_validator as run_validator

    run_validator()


def show_foreign_key_validator():
    from tools.foreign_key_validator import show_foreign_key_validator as run_validator

    run_validator()


def show_lookup_update():
    st.title("🔍 Lookup & Update")
    st.markdown("Perform lookup operations and update data between Excel files.")

    st.info(
        "🚧 **Coming Soon** - This tool will enable VLOOKUP-style operations between different Excel files."
    )

    with st.expander("ℹ️ How this tool will work"):
        st.markdown(
            """
        1. **Upload Source File**: The file containing data to lookup
        2. **Upload Target File**: The file to be updated
        3. **Map Columns**: Define lookup and update relationships
        4. **Configure Options**: Set match criteria and update behavior
        5. **Preview Changes**: Review updates before applying
        6. **Download Results**: Get your updated Excel file
        """
        )


def show_data_merger():
    st.title("📊 Data Merger")
    st.markdown("Merge data from multiple Excel files intelligently.")

    st.info(
        "🚧 **Coming Soon** - Combine multiple Excel files with conflict resolution."
    )


def show_sheet_comparer():
    st.title("⚖️ Sheet Comparer")
    st.markdown("Compare data between different sheets or workbooks.")

    st.info(
        "🚧 **Coming Soon** - Generate detailed comparison reports between datasets."
    )


def show_duplicate_detector():
    st.title("🔄 Duplicate Detector")
    st.markdown("Find and highlight duplicate records in your data.")

    st.info(
        "🚧 **Coming Soon** - Flexible duplicate detection with customizable matching rules."
    )


if __name__ == "__main__":
    main()
