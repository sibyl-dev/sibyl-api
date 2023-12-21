import streamlit as st
import ruamel.yaml as yaml
import os
import pandas as pd


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "")


def show_table(df, key=None, column_config=None):
    return st.data_editor(
        df,
        key=key,
        hide_index=True,
        num_rows="dynamic",
        disabled=False,
        column_config=column_config,
    )


def _validate_entities(_):
    return True


def _validate_features(feature_df):
    # Return False if features has any column except name or type
    required_cols = ["name", "type"]
    missing_cols = [col for col in required_cols if col not in feature_df.columns]
    if len(missing_cols) > 0:
        st.error(f"Features file is missing required columns: {missing_cols}")
        return False
    return True


def _validate_categories(category_df):
    if "name" not in category_df.columns:
        st.error("Categories file is missing required column: name")
        return False


def upload_file(term, validate_func):
    csv = st.file_uploader(f"Upload {term} file", type="csv")
    df = None
    if csv is not None:
        df = pd.read_csv(csv)
        validate_func(df)
    return df


def entity_configs():
    entity_df = upload_file("entities", _validate_entities)
    if entity_df is not None:
        return show_table(entity_df, key=f"entity_editor")
    else:
        return st.info(f"Upload entity csv above to start editing")


def feature_configs():
    feature_df = upload_file("features", _validate_features)
    if feature_df is not None:
        column_config = {
            "type": st.column_config.SelectboxColumn(
                options=["categorical", "numerical", "boolean"]
            ),
            "category": st.column_config.SelectboxColumn(options=feature_df["category"].unique()),
        }
        result_df = show_table(feature_df, key=f"feature_editor", column_config=column_config)
        return result_df
    else:
        st.info(f"Upload a feature csv above to start editing")
        return None


def main():
    st.set_page_config(layout="wide")

    loader = yaml.YAML()
    # loader.add_representer(type(None), represent_none)

    st.title("Configuration Wizard")

    entities_tab, features_tab, context_tab = st.tabs(["Entities", "Features", "Context"])
    with entities_tab:
        entity_configs()

    with features_tab:
        feature_configs()

    with context_tab:
        # Load existing configuration if available
        existing_config = load_existing_config(loader)

        with st.form("config_form"):
            config_data = dict()

            # Question 2: Use Multiple Rows
            config_data["USE_MULTIPLE_ROWS"] = st.radio(
                "Does your data have multiple rows?", ["Yes", "No"], horizontal=True
            )

            if config_data["USE_MULTIPLE_ROWS"] == "Yes":
                config_data["ROW_LABEL"] = st.text_input(
                    "How should we label rows?", value="Timestamp"
                )

            config_data["BAR_LENGTH"] = st.number_input(
                "What is the length of the bar?", min_value=0, max_value=10, value=8
            )

            with st.expander("Modify terms"):
                terms = [
                    ("Entity", "Label of whatever is being predicted on"),
                    ("Feature", ""),
                    ("Positive", "Features that increase the model output"),
                    ("Negative", "Features that decrease the model output"),
                ]
                for term, helper in terms:
                    st.text_input(term, max_chars=15, placeholder=helper)

            submitted = st.form_submit_button("Save config")

        if submitted:
            save_config(loader, config_data, existing_config)


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists("config.yml"):
        with open("config.yml", "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    loader.default_flow_style = False

    existing_config.update(config_data)

    with open("config2.yml", "w") as yaml_file:
        loader.dump(existing_config, yaml_file)
    st.success("Configuration saved successfully!")


if __name__ == "__main__":
    main()
