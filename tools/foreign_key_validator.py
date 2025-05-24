import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple, Any
from utils.excel_handler import ExcelHandler


class ForeignKeyValidator:
    """Foreign Key Validator tool for validating foreign key relationships in Excel files."""

    def __init__(self):
        self.excel_handler = ExcelHandler()

    def run(self):
        """Main function to run the Foreign Key Validator tool."""
        st.title("🔗 Foreign Key Validator")
        st.markdown("Validate foreign key relationships across Excel files or sheets.")

        # Step 1: File Upload for Parent Table
        st.subheader("📁 Step 1: Upload Parent Table (Reference Data)")
        parent_file = st.file_uploader(
            "Choose Excel file containing parent/reference data",
            type=["xlsx", "xls"],
            key="parent_file",
            help="Upload the Excel file containing the reference data (parent table)",
        )

        if parent_file is not None:
            # Validate parent file
            is_valid, message = self.excel_handler.validate_file(parent_file)
            if not is_valid:
                st.error(f"❌ {message}")
                return
            st.success(f"✅ Parent file: {message}")

            # Parent file skip rows configuration
            st.subheader("📏 Step 1.5: Parent Table Header Configuration")
            col1, col2 = st.columns([2, 1])
            with col1:
                parent_skip_rows = st.number_input(
                    "Number of rows to skip before header (Parent)",
                    min_value=0,
                    max_value=50,
                    value=0,
                    key="parent_skip",
                    help="Skip this many rows from the top before treating the next row as headers",
                )
            with col2:
                st.info(f"Parent header row: **Row {parent_skip_rows + 1}**")

            # Preview parent data
            if st.checkbox("📋 Preview parent data structure", key="preview_parent"):
                self._show_data_preview(parent_file, parent_skip_rows, "Parent")

            # Read parent data
            with st.spinner("Reading parent Excel file..."):
                parent_sheets_data = self.excel_handler.read_excel_file(
                    parent_file, parent_skip_rows
                )

            if not parent_sheets_data:
                st.error("Failed to read the parent Excel file")
                return

            # Step 2: Parent Sheet Selection
            st.subheader("📋 Step 2: Select Parent Sheet")
            parent_sheet_names = list(parent_sheets_data.keys())

            if len(parent_sheet_names) == 1:
                selected_parent_sheet = parent_sheet_names[0]
                st.info(f"Using parent sheet: **{selected_parent_sheet}**")
            else:
                selected_parent_sheet = st.selectbox(
                    "Choose parent sheet:",
                    parent_sheet_names,
                    key="parent_sheet",
                    help="Select the sheet containing the reference data",
                )

            parent_df = parent_sheets_data[selected_parent_sheet]
            self._display_dataframe_info(parent_df, "Parent Table")

            # Step 3: File Upload for Child Table
            st.subheader("📁 Step 3: Upload Child Table (Data to Validate)")

            # Option to use same file or different file
            use_same_file = st.checkbox(
                "Use same file for child table",
                help="Check this if both parent and child data are in the same Excel file",
            )

            if use_same_file:
                child_file = parent_file
                child_sheets_data = parent_sheets_data
                child_skip_rows = parent_skip_rows
                st.info("Using the same file for child table")
            else:
                child_file = st.file_uploader(
                    "Choose Excel file containing child data",
                    type=["xlsx", "xls"],
                    key="child_file",
                    help="Upload the Excel file containing the data to validate (child table)",
                )

                if child_file is None:
                    st.warning("Please upload the child table file to continue.")
                    return

                # Validate child file
                is_valid, message = self.excel_handler.validate_file(child_file)
                if not is_valid:
                    st.error(f"❌ {message}")
                    return
                st.success(f"✅ Child file: {message}")

                # Child file skip rows configuration
                st.subheader("📏 Step 3.5: Child Table Header Configuration")
                col1, col2 = st.columns([2, 1])
                with col1:
                    child_skip_rows = st.number_input(
                        "Number of rows to skip before header (Child)",
                        min_value=0,
                        max_value=50,
                        value=0,
                        key="child_skip",
                        help="Skip this many rows from the top before treating the next row as headers",
                    )
                with col2:
                    st.info(f"Child header row: **Row {child_skip_rows + 1}**")

                # Preview child data
                if st.checkbox("📋 Preview child data structure", key="preview_child"):
                    self._show_data_preview(child_file, child_skip_rows, "Child")

                # Read child data
                with st.spinner("Reading child Excel file..."):
                    child_sheets_data = self.excel_handler.read_excel_file(
                        child_file, child_skip_rows
                    )

                if not child_sheets_data:
                    st.error("Failed to read the child Excel file")
                    return

            # Step 4: Child Sheet Selection
            st.subheader("📋 Step 4: Select Child Sheet")
            child_sheet_names = list(child_sheets_data.keys())

            if len(child_sheet_names) == 1:
                selected_child_sheet = child_sheet_names[0]
                st.info(f"Using child sheet: **{selected_child_sheet}**")
            else:
                selected_child_sheet = st.selectbox(
                    "Choose child sheet:",
                    child_sheet_names,
                    key="child_sheet",
                    help="Select the sheet containing the data to validate",
                )

            child_df = child_sheets_data[selected_child_sheet]
            self._display_dataframe_info(child_df, "Child Table")

            # Step 5: Foreign Key Relationship Configuration
            st.subheader("🔗 Step 5: Configure Foreign Key Relationship")

            parent_columns = self.excel_handler.get_column_names(parent_df)
            child_columns = self.excel_handler.get_column_names(child_df)

            # Parent key selection
            st.write("**Parent Table Primary Key:**")
            parent_key_type = st.radio(
                "Parent key type:",
                ["Single Column", "Composite Key"],
                key="parent_key_type",
                help="Choose whether the parent key consists of one or multiple columns",
            )

            if parent_key_type == "Single Column":
                parent_key_columns = [
                    st.selectbox(
                        "Select parent key column:",
                        parent_columns,
                        key="parent_key_single",
                        help="Choose the primary key column in the parent table",
                    )
                ]
            else:
                parent_key_columns = st.multiselect(
                    "Select parent key columns:",
                    parent_columns,
                    key="parent_key_multi",
                    help="Choose multiple columns that form the composite primary key",
                )

            # Child key selection
            st.write("**Child Table Foreign Key:**")
            child_key_type = st.radio(
                "Child key type:",
                ["Single Column", "Composite Key"],
                key="child_key_type",
                help="Choose whether the foreign key consists of one or multiple columns",
            )

            if child_key_type == "Single Column":
                child_key_columns = [
                    st.selectbox(
                        "Select foreign key column:",
                        child_columns,
                        key="child_key_single",
                        help="Choose the foreign key column in the child table",
                    )
                ]
            else:
                child_key_columns = st.multiselect(
                    "Select foreign key columns:",
                    child_columns,
                    key="child_key_multi",
                    help="Choose multiple columns that form the composite foreign key",
                )

            if not parent_key_columns or not child_key_columns:
                st.warning("Please select both parent and child key columns.")
                return

            if len(parent_key_columns) != len(child_key_columns):
                st.error("Parent and child key must have the same number of columns.")
                return

            # Step 6: Validation Options
            st.subheader("⚙️ Step 6: Validation Options")

            col1, col2, col3 = st.columns(3)

            with col1:
                ignore_empty = st.checkbox(
                    "Ignore empty/null values",
                    value=True,
                    help="Skip validation for rows where foreign key columns contain empty or null values",
                )

            with col2:
                case_sensitive = st.checkbox(
                    "Case sensitive comparison",
                    value=True,
                    help="Treat 'ABC' and 'abc' as different values",
                )

            with col3:
                allow_nulls = st.checkbox(
                    "Allow NULL foreign keys",
                    value=True,
                    help="Consider NULL/empty foreign keys as valid (optional relationship)",
                )

            # Step 7: Run Validation
            st.subheader("🚀 Step 7: Run Validation")

            if st.button("🔍 Validate Foreign Keys", type="primary"):
                with st.spinner("Validating foreign key relationships..."):
                    results = self.validate_foreign_keys(
                        parent_df,
                        child_df,
                        parent_key_columns,
                        child_key_columns,
                        ignore_empty,
                        case_sensitive,
                        allow_nulls,
                    )

                self.display_results(
                    results, parent_df, child_df, parent_key_columns, child_key_columns
                )

    def _show_data_preview(self, file, skip_rows: int, table_type: str):
        """Show data preview for uploaded file"""
        with st.spinner(f"Loading {table_type.lower()} preview..."):
            try:
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Raw {table_type} Data (first 10 rows):**")
                    raw_preview = self.excel_handler.preview_raw_excel(file, 10)
                    if not raw_preview.empty:
                        raw_preview.index = [
                            f"Row {i+1}" for i in range(len(raw_preview))
                        ]
                        st.dataframe(raw_preview, use_container_width=True)

                with col2:
                    st.write(
                        f"**Processed {table_type} Data (skipping {skip_rows} rows):**"
                    )
                    processed_preview = pd.read_excel(
                        file,
                        sheet_name=0,
                        engine="openpyxl",
                        skiprows=skip_rows,
                        nrows=5,
                    )
                    st.dataframe(processed_preview, use_container_width=True)

                    st.write("**Detected Column Headers:**")
                    headers_text = ", ".join(
                        [f"'{col}'" for col in processed_preview.columns.astype(str)]
                    )
                    st.code(headers_text)

            except Exception as e:
                st.error(f"Error previewing {table_type.lower()} data: {str(e)}")

    def _display_dataframe_info(self, df: pd.DataFrame, table_name: str):
        """Display basic information about a dataframe"""
        info = self.excel_handler.get_dataframe_info(df)
        st.write(f"**{table_name} Information:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", info["rows"])
        with col2:
            st.metric("Columns", len(info["columns"]))
        with col3:
            st.metric("Memory", f"{info['memory_usage'] / 1024:.1f} KB")

    def validate_foreign_keys(
        self,
        parent_df: pd.DataFrame,
        child_df: pd.DataFrame,
        parent_key_columns: List[str],
        child_key_columns: List[str],
        ignore_empty: bool,
        case_sensitive: bool,
        allow_nulls: bool,
    ) -> Dict[str, Any]:
        """
        Validate foreign key relationships between parent and child tables

        Args:
            parent_df: Parent table DataFrame
            child_df: Child table DataFrame
            parent_key_columns: List of parent key column names
            child_key_columns: List of child key column names
            ignore_empty: Whether to ignore empty/null values during processing
            case_sensitive: Whether comparison should be case sensitive
            allow_nulls: Whether to allow NULL foreign keys

        Returns:
            Dictionary containing validation results
        """
        # Create working copies
        parent_work = parent_df.copy()
        child_work = child_df.copy()

        # Handle case sensitivity
        if not case_sensitive:
            for col in parent_key_columns:
                if parent_work[col].dtype == "object":
                    parent_work[col] = parent_work[col].astype(str).str.lower()

            for col in child_key_columns:
                if child_work[col].dtype == "object":
                    child_work[col] = child_work[col].astype(str).str.lower()

        # Create composite keys
        if len(parent_key_columns) == 1:
            parent_work["_parent_key"] = parent_work[parent_key_columns[0]]
        else:
            parent_work["_parent_key"] = (
                parent_work[parent_key_columns]
                .astype(str)
                .apply(lambda x: "|".join(x), axis=1)
            )

        if len(child_key_columns) == 1:
            child_work["_child_key"] = child_work[child_key_columns[0]]
        else:
            child_work["_child_key"] = (
                child_work[child_key_columns]
                .astype(str)
                .apply(lambda x: "|".join(x), axis=1)
            )

        # Get unique parent keys (excluding empty if needed)
        if ignore_empty:
            parent_mask = pd.Series([True] * len(parent_work))
            for col in parent_key_columns:
                parent_mask &= ~(
                    parent_df[col].isna()
                    | (parent_df[col].astype(str).str.strip() == "")
                )
            valid_parent_keys = set(parent_work[parent_mask]["_parent_key"].unique())
        else:
            valid_parent_keys = set(parent_work["_parent_key"].unique())

        # Filter child records for validation
        child_validation_mask = pd.Series([True] * len(child_work))

        if ignore_empty or allow_nulls:
            # Identify rows with empty/null foreign keys
            null_mask = pd.Series([False] * len(child_work))
            for col in child_key_columns:
                null_mask |= child_df[col].isna() | (
                    child_df[col].astype(str).str.strip() == ""
                )

            if allow_nulls:
                # If nulls are allowed, exclude them from validation but count them separately
                child_validation_mask = ~null_mask
                null_foreign_keys = child_work[null_mask].copy()
            else:
                # If ignoring empty, exclude them from validation
                child_validation_mask = ~null_mask
                null_foreign_keys = pd.DataFrame()
        else:
            null_foreign_keys = pd.DataFrame()

        # Get child records to validate
        child_to_validate = child_work[child_validation_mask].copy()

        # Find orphaned records (foreign keys not in parent)
        if len(child_to_validate) > 0:
            orphaned_mask = ~child_to_validate["_child_key"].isin(valid_parent_keys)
            orphaned_records = child_to_validate[orphaned_mask].copy()
        else:
            orphaned_records = pd.DataFrame()

        # Find valid relationships
        if len(child_to_validate) > 0:
            valid_mask = child_to_validate["_child_key"].isin(valid_parent_keys)
            valid_records = child_to_validate[valid_mask].copy()
        else:
            valid_records = pd.DataFrame()

        # Group orphaned records by foreign key value
        orphaned_groups = []
        if len(orphaned_records) > 0:
            for key_value in orphaned_records["_child_key"].unique():
                group_df = orphaned_records[orphaned_records["_child_key"] == key_value]
                orphaned_groups.append(
                    {
                        "key_value": key_value,
                        "count": len(group_df),
                        "rows": group_df.index.tolist(),
                        "data": child_df.loc[group_df.index],  # Original data
                    }
                )

        # Calculate statistics
        total_child_rows = len(child_df)
        validated_rows = len(child_to_validate)
        null_rows = len(null_foreign_keys)
        valid_relationships = len(valid_records)
        orphaned_rows = len(orphaned_records)
        unique_parent_keys = len(valid_parent_keys)

        return {
            "is_valid": len(orphaned_records) == 0,
            "total_child_rows": total_child_rows,
            "validated_rows": validated_rows,
            "null_foreign_keys": null_rows,
            "valid_relationships": valid_relationships,
            "orphaned_count": orphaned_rows,
            "unique_orphaned_keys": len(orphaned_groups),
            "unique_parent_keys": unique_parent_keys,
            "orphaned_groups": orphaned_groups,
            "orphaned_records": (
                child_df.loc[orphaned_records.index]
                if len(orphaned_records) > 0
                else pd.DataFrame()
            ),
            "null_records": (
                child_df.loc[null_foreign_keys.index]
                if len(null_foreign_keys) > 0
                else pd.DataFrame()
            ),
            "orphaned_row_indices": (
                orphaned_records.index.tolist() if len(orphaned_records) > 0 else []
            ),
        }

    def display_results(
        self,
        results: Dict[str, Any],
        parent_df: pd.DataFrame,
        child_df: pd.DataFrame,
        parent_key_columns: List[str],
        child_key_columns: List[str],
    ):
        """Display validation results"""

        # Results Summary
        st.subheader("📊 Validation Results")

        if results["is_valid"]:
            st.success("🎉 **All foreign key relationships are valid!**")
        else:
            st.error(
                f"❌ **Found {results['orphaned_count']} orphaned records with {results['unique_orphaned_keys']} unique foreign key value(s)**"
            )

        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Child Rows", results["total_child_rows"])

        with col2:
            st.metric("Validated Rows", results["validated_rows"])

        with col3:
            st.metric("Valid Relationships", results["valid_relationships"])

        with col4:
            st.metric("Orphaned Records", results["orphaned_count"])

        with col5:
            st.metric("NULL Foreign Keys", results["null_foreign_keys"])

        # Additional stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Unique Parent Keys", results["unique_parent_keys"])
        with col2:
            validity_percentage = (
                (results["valid_relationships"] / results["validated_rows"] * 100)
                if results["validated_rows"] > 0
                else 0
            )
            st.metric("Validity Rate", f"{validity_percentage:.1f}%")

        # Show orphaned records if any
        if not results["is_valid"]:
            st.subheader("🚨 Orphaned Records")

            # Show orphaned groups
            for i, group in enumerate(results["orphaned_groups"], 1):
                with st.expander(
                    f"Orphaned Group {i}: Foreign Key '{group['key_value']}' ({group['count']} records)"
                ):
                    display_columns = (
                        child_key_columns
                        + [
                            col
                            for col in group["data"].columns
                            if col not in child_key_columns
                        ][:8]
                    )  # Limit columns for display
                    st.dataframe(
                        group["data"][display_columns],
                        use_container_width=True,
                    )

            # Full orphaned records table
            st.subheader("📋 All Orphaned Records")
            if len(results["orphaned_records"]) > 0:
                st.dataframe(results["orphaned_records"], use_container_width=True)

        # Show NULL foreign keys if any
        if len(results["null_records"]) > 0:
            st.subheader("🔍 Records with NULL Foreign Keys")
            with st.expander(
                f"Show {len(results['null_records'])} records with NULL foreign keys"
            ):
                st.dataframe(results["null_records"], use_container_width=True)

        # Download options
        if not results["is_valid"] or len(results["null_records"]) > 0:
            st.subheader("💾 Download Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                if len(results["orphaned_records"]) > 0:
                    # Download orphaned records
                    orphaned_excel = self.excel_handler.create_download_excel(
                        {"Orphaned_Records": results["orphaned_records"]},
                        "orphaned_records.xlsx",
                    )

                    st.download_button(
                        label="📥 Download Orphaned Records",
                        data=orphaned_excel,
                        file_name="orphaned_records.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

            with col2:
                if len(results["null_records"]) > 0:
                    # Download NULL foreign key records
                    null_excel = self.excel_handler.create_download_excel(
                        {"NULL_Foreign_Keys": results["null_records"]},
                        "null_foreign_keys.xlsx",
                    )

                    st.download_button(
                        label="📥 Download NULL Foreign Keys",
                        data=null_excel,
                        file_name="null_foreign_keys.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

            with col3:
                if len(results["orphaned_row_indices"]) > 0:
                    # Download child data with orphaned records highlighted
                    highlighted_excel = self.excel_handler.create_highlighted_excel(
                        child_df,
                        results["orphaned_row_indices"],
                        "Child_Data_with_Orphaned_Highlighted",
                        "FF6B6B",  # Red highlight for orphaned records
                    )

                    st.download_button(
                        label="📥 Download Highlighted Data",
                        data=highlighted_excel,
                        file_name="child_data_with_orphaned_highlighted.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

        else:
            # No issues found - show sample data
            st.subheader("📋 Data Preview")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Parent Table Preview:**")
                parent_preview = self.excel_handler.preview_dataframe(parent_df, 5)
                st.dataframe(parent_preview, use_container_width=True)

            with col2:
                st.write("**Child Table Preview:**")
                child_preview = self.excel_handler.preview_dataframe(child_df, 5)
                st.dataframe(child_preview, use_container_width=True)

            st.info("✅ All foreign key relationships are valid!")


# Function to integrate with main app
def show_foreign_key_validator():
    """Function to be called from main app"""
    validator = ForeignKeyValidator()
    validator.run()
