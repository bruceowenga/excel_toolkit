import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple, Any
from utils.excel_handler import ExcelHandler


class PrimaryKeyValidator:
    """Primary Key Validator tool for checking uniqueness of keys in Excel data"""

    def __init__(self):
        self.excel_handler = ExcelHandler()

    def run(self):
        """Main function to run the Primary Key Validator interface"""
        st.title("🔑 Primary Key Validator")
        st.markdown("Validate the uniqueness of primary keys in your Excel data.")

        # Step 1: File Upload
        st.subheader("📁 Step 1: Upload Excel File")
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=["xlsx", "xls"],
            help="Upload the Excel file you want to validate",
        )

        if uploaded_file is not None:
            # Validate the file
            is_valid, message = self.excel_handler.validate_file(uploaded_file)

            if not is_valid:
                st.error(f"❌ {message}")
                return

            st.success(f"✅ {message}")

            # Step 1.5: Skip Rows Option
            st.subheader("📏 Step 1.5: Header Row Configuration")

            col1, col2 = st.columns([2, 1])
            with col1:
                skip_rows = st.number_input(
                    "Number of rows to skip before header",
                    min_value=0,
                    max_value=50,
                    value=0,
                    help="Skip this many rows from the top before treating the next row as headers",
                )

            with col2:
                st.info(f"Header row will be: **Row {skip_rows + 1}**")

            if skip_rows > 0:
                st.warning(
                    f"⚠️ Skipping the first {skip_rows} row(s). The header row will be row {skip_rows + 1}."
                )

            # Preview option
            if st.checkbox(
                "📋 Preview data structure",
                help="See how your data looks with current skip row setting",
            ):
                with st.spinner("Loading preview..."):
                    try:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Raw Data (first 10 rows):**")
                            raw_preview = self.excel_handler.preview_raw_excel(
                                uploaded_file, 10
                            )
                            if not raw_preview.empty:
                                # Add row numbers for reference
                                raw_preview.index = [
                                    f"Row {i+1}" for i in range(len(raw_preview))
                                ]
                                st.dataframe(raw_preview, use_container_width=True)

                        with col2:
                            st.write(f"**Processed Data (skipping {skip_rows} rows):**")
                            processed_preview = pd.read_excel(
                                uploaded_file,
                                sheet_name=0,
                                engine="openpyxl",
                                skiprows=skip_rows,
                                nrows=5,  # Only read first 5 rows for preview
                            )
                            st.dataframe(processed_preview, use_container_width=True)

                            st.write("**Detected Column Headers:**")
                            headers_text = ", ".join(
                                [
                                    f"'{col}'"
                                    for col in processed_preview.columns.astype(str)
                                ]
                            )
                            st.code(headers_text)

                    except Exception as e:
                        st.error(f"Error previewing data: {str(e)}")

            # Read the Excel file
            with st.spinner("Reading Excel file..."):
                sheets_data = self.excel_handler.read_excel_file(
                    uploaded_file, skip_rows
                )

            if not sheets_data:
                st.error("Failed to read the Excel file")
                return

            # Step 2: Sheet Selection
            st.subheader("📋 Step 2: Select Sheet")
            sheet_names = list(sheets_data.keys())

            if len(sheet_names) == 1:
                selected_sheet = sheet_names[0]
                st.info(f"Using sheet: **{selected_sheet}**")
            else:
                selected_sheet = st.selectbox(
                    "Choose a sheet to validate:",
                    sheet_names,
                    help="Select the sheet containing the data to validate",
                )

            df = sheets_data[selected_sheet]

            # Display basic info about the data
            info = self.excel_handler.get_dataframe_info(df)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", info["rows"])
            with col2:
                st.metric("Total Columns", len(info["columns"]))
            with col3:
                st.metric("Memory Usage", f"{info['memory_usage'] / 1024:.1f} KB")

            # Step 3: Primary Key Selection
            st.subheader("🔑 Step 3: Select Primary Key Column(s)")

            available_columns = self.excel_handler.get_column_names(df)

            # Option for single or composite primary key
            key_type = st.radio(
                "Primary Key Type:",
                ["Single Column", "Composite Key (Multiple Columns)"],
                help="Choose whether your primary key consists of one column or multiple columns",
            )

            if key_type == "Single Column":
                primary_key_columns = [
                    st.selectbox(
                        "Select primary key column:",
                        available_columns,
                        help="Choose the column that should contain unique values",
                    )
                ]
            else:
                primary_key_columns = st.multiselect(
                    "Select primary key columns:",
                    available_columns,
                    help="Choose multiple columns that together form a unique key",
                )

            if not primary_key_columns:
                st.warning("Please select at least one primary key column.")
                return

            # Step 4: Validation Options
            st.subheader("⚙️ Step 4: Validation Options")

            col1, col2 = st.columns(2)
            with col1:
                ignore_empty = st.checkbox(
                    "Ignore empty/null values",
                    value=True,
                    help="Skip rows where primary key columns contain empty or null values",
                )

            with col2:
                case_sensitive = st.checkbox(
                    "Case sensitive comparison",
                    value=True,
                    help="Treat 'ABC' and 'abc' as different values",
                )

            # Step 5: Run Validation
            st.subheader("🚀 Step 5: Run Validation")

            if st.button("🔍 Validate Primary Keys", type="primary"):
                with st.spinner("Validating primary keys..."):
                    results = self.validate_primary_keys(
                        df, primary_key_columns, ignore_empty, case_sensitive
                    )

                self.display_results(results, df, primary_key_columns)

    def validate_primary_keys(
        self,
        df: pd.DataFrame,
        pk_columns: List[str],
        ignore_empty: bool,
        case_sensitive: bool,
    ) -> Dict[str, Any]:
        """
        Validate primary key uniqueness

        Args:
            df: DataFrame to validate
            pk_columns: List of primary key column names
            ignore_empty: Whether to ignore empty/null values
            case_sensitive: Whether comparison should be case sensitive

        Returns:
            Dictionary containing validation results
        """
        # Create a copy for processing
        work_df = df.copy()

        # Handle case sensitivity
        if not case_sensitive:
            for col in pk_columns:
                if work_df[col].dtype == "object":  # String columns
                    work_df[col] = work_df[col].astype(str).str.lower()

        # Create composite key if multiple columns
        if len(pk_columns) == 1:
            key_column = pk_columns[0]
            work_df["_primary_key"] = work_df[key_column]
        else:
            # Combine multiple columns into a single key
            work_df["_primary_key"] = (
                work_df[pk_columns].astype(str).apply(lambda x: "|".join(x), axis=1)
            )

        # Handle empty values
        if ignore_empty:
            # Remove rows where any primary key column is empty/null
            mask = pd.Series([True] * len(work_df))
            for col in pk_columns:
                mask &= ~(df[col].isna() | (df[col].astype(str).str.strip() == ""))

            filtered_df = work_df[mask].copy()
            ignored_rows = len(work_df) - len(filtered_df)
        else:
            filtered_df = work_df.copy()
            ignored_rows = 0

        # Find duplicates
        duplicate_mask = filtered_df.duplicated(subset=["_primary_key"], keep=False)
        duplicates_df = filtered_df[duplicate_mask].copy()

        # Get original row indices for highlighting
        if ignore_empty:
            original_indices = work_df[mask][duplicate_mask].index.tolist()
        else:
            original_indices = duplicates_df.index.tolist()

        # Group duplicates
        duplicate_groups = []
        if len(duplicates_df) > 0:
            for key_value in duplicates_df["_primary_key"].unique():
                group_df = duplicates_df[duplicates_df["_primary_key"] == key_value]
                duplicate_groups.append(
                    {
                        "key_value": key_value,
                        "count": len(group_df),
                        "rows": group_df.index.tolist(),
                        "data": df.loc[group_df.index],  # Original data
                    }
                )

        return {
            "is_valid": len(duplicates_df) == 0,
            "total_rows": len(df),
            "validated_rows": len(filtered_df),
            "ignored_rows": ignored_rows,
            "duplicate_count": len(duplicates_df),
            "unique_duplicate_keys": len(duplicate_groups),
            "duplicate_groups": duplicate_groups,
            "duplicate_row_indices": original_indices,
        }

    def display_results(
        self, results: Dict[str, Any], df: pd.DataFrame, pk_columns: List[str]
    ):
        """Display validation results"""

        # Results Summary
        st.subheader("📊 Validation Results")

        if results["is_valid"]:
            st.success("🎉 **All primary keys are unique!**")
        else:
            st.error(
                f"❌ **Found {results['duplicate_count']} duplicate records with {results['unique_duplicate_keys']} unique key value(s)**"
            )

        # Statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Rows", results["total_rows"])

        with col2:
            st.metric("Validated Rows", results["validated_rows"])

        with col3:
            st.metric("Ignored Rows", results["ignored_rows"])

        with col4:
            st.metric("Duplicate Records", results["duplicate_count"])

        # Show duplicates if any
        if not results["is_valid"]:
            st.subheader("🔍 Duplicate Records")

            # Show duplicate groups
            for i, group in enumerate(results["duplicate_groups"], 1):
                with st.expander(
                    f"Duplicate Group {i}: Key '{group['key_value']}' ({group['count']} records)"
                ):
                    st.dataframe(
                        group["data"][
                            pk_columns
                            + [
                                col
                                for col in group["data"].columns
                                if col not in pk_columns
                            ][:5]
                        ],
                        use_container_width=True,
                    )

            # Full duplicate records table
            st.subheader("📋 All Duplicate Records")
            all_duplicates = pd.concat(
                [group["data"] for group in results["duplicate_groups"]],
                ignore_index=False,
            )
            st.dataframe(all_duplicates, use_container_width=True)

            # Download options
            st.subheader("💾 Download Results")

            col1, col2 = st.columns(2)

            with col1:
                # Download duplicates only
                duplicates_excel = self.excel_handler.create_download_excel(
                    {"Duplicates": all_duplicates}, "duplicate_records.xlsx"
                )

                st.download_button(
                    label="📥 Download Duplicate Records",
                    data=duplicates_excel,
                    file_name="duplicate_records.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with col2:
                # Download full data with highlights
                highlighted_excel = self.excel_handler.create_highlighted_excel(
                    df,
                    results["duplicate_row_indices"],
                    "Data_with_Duplicates_Highlighted",
                    "FFFF00",  # Yellow highlight
                )

                st.download_button(
                    label="📥 Download Highlighted Data",
                    data=highlighted_excel,
                    file_name="data_with_duplicates_highlighted.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        else:
            # No duplicates - show sample data
            st.subheader("📋 Data Preview")
            preview_df = self.excel_handler.preview_dataframe(df, 10)
            st.dataframe(preview_df, use_container_width=True)

            if len(df) > 10:
                st.info(f"Showing first 10 rows of {len(df)} total rows")


# Function to integrate with main app
def show_primary_key_validator():
    """Function to be called from main app"""
    validator = PrimaryKeyValidator()
    validator.run()
