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


def _validate_entities(entity_df):
    if entity_df is None or entity_df.empty:
        st.error("Invalid or empty file found")
        return False
    return True


def _validate_features(feature_df):
    # Return False if features has any column except name or type
    required_cols = ["name", "type"]
    missing_cols = [col for col in required_cols if col not in feature_df.columns]
    if len(missing_cols) > 0:
        st.error(f"Features file is missing required columns: {missing_cols}")
        return False
    return True


def upload_file(term, validate_func):
    csv = st.file_uploader(f"Upload {term} file", type="csv")
    df = None
    if csv is not None:
        df = pd.read_csv(csv)
        if not validate_func(df):
            return None
    return df


def entity_configs():
    st.header("Prepare Entities")
    entity_df = upload_file("entities", _validate_entities)
    if entity_df is not None:
        with st.expander("Edit entities"):
            entity_df = show_table(entity_df)
        return entity_df
    else:
        st.info(f"Upload entity csv above to start editing")
        return None


def feature_configs():
    st.header("Prepare Features")
    feature_df = upload_file("features", _validate_features)
    if feature_df is not None:
        column_config = {
            "type": st.column_config.SelectboxColumn(
                options=["categorical", "numerical", "boolean"]
            ),
            "category": st.column_config.SelectboxColumn(options=feature_df["category"].unique()),
        }
        with st.expander("Edit features"):
            result_df = show_table(feature_df, key=f"feature_editor", column_config=column_config)
        return result_df
    else:
        st.info(f"Upload a feature csv above to start editing")
        return None


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists("config.yml"):
        with open("context_config.yml", "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    loader.default_flow_style = False
    existing_config.update(config_data)

    with open("context_config.yml", "w") as yaml_file:
        loader.dump(existing_config, yaml_file)
    st.success("Configuration saved successfully!")


def context_configs():
    st.header("Configure Context")
    loader = yaml.YAML()

    # Load existing configuration if available
    existing_config = load_existing_config(loader)

    config_data = dict()

    use_rows = st.radio("Does your data have multiple rows?", ["Yes", "No"], horizontal=True)
    config_data["use_rows"] = True if use_rows == "Yes" else False

    if config_data["use_rows"]:
        config_data["row_label"] = st.text_input("How should we label rows?", max_chars=25)

    output_type = st.radio(
        "What is your model's output type?", ["Numeric", "Boolean", "Categorical"], horizontal=True
    )
    config_data["output_type"] = output_type.lower()

    if config_data["output_type"] == "boolean":
        config_data["output_pos_label"] = st.text_input(
            "How should we label positive predictions?", max_chars=25
        )
        config_data["output_neg_label"] = st.text_input(
            "How should we label negative predictions?", max_chars=25
        )
    if config_data["output_type"] == "numeric":
        output_format_string = st.radio(
            "How should we format the output?",
            ["1,234", "1,234.56", "$1,234", "$1,234.56", "No Formatting", "Custom"],
            horizontal=True,
        )
        if output_format_string == "Custom":
            config_data["output_format_string"] = st.text_input(
                "How should we format the output (python f-string)?"
            )
        elif output_format_string != "No Formatting":
            formats = {
                "$1,234": "${:,.0f}",
                "$1,234.56": "${:,.2f}",
                "1,234": "{:,.0f}",
                "1,234.56": "{:,.2f}",
            }
            config_data["output_format_string"] = formats[output_format_string]

    output_sentiment_is_negative = st.radio(
        "Does an increasing model prediction refer to a positive or negative outcome?",
        ["Positive", "Negative", "Neither"],
        horizontal=True,
    )
    config_data["output_sentiment_is_negative"] = (
        True
        if output_sentiment_is_negative == "Negative"
        else False if output_sentiment_is_negative == "Positive" else None
    )

    with st.expander("Modify terms"):
        terms = [
            ("Entity", "Label of whatever is being predicted on"),
            ("Feature", ""),
            ("Positive", "Features that increase the model output"),
            ("Negative", "Features that decrease the model output"),
        ]
        config_data["terms"] = dict()
        for term, helper in terms:
            config_data["terms"][term] = st.text_input(term, max_chars=15, placeholder=helper)

    return config_data


def main():
    # st.set_page_config(layout="wide")

    # loader.add_representer(type(None), represent_none)

    st.title("Configuration Wizard")

    entity_df = entity_configs()
    if entity_df is not None:
        st.divider()
        feature_df = feature_configs()
        if feature_df is not None:
            st.divider()
            context = context_configs()


if __name__ == "__main__":
    main()