import os
import pickle

import pandas as pd
import ruamel.yaml as yaml
import streamlit as st
from pyreal import RealApp

from sibyl.db import preprocessing as db


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


def upload_csv(term, validate_func):
    csv = st.file_uploader(f"Upload {term} file", type="csv", key=f"{term}_file")
    df = None
    if csv is not None:
        df = pd.read_csv(csv)
        if not validate_func(df):
            return None
    return df


def entity_configs():
    st.header("Prepare Entities")
    entity_df = upload_csv("entities", _validate_entities)
    if entity_df is not None:
        label_column = st.selectbox(
            "What is your label column (y-values)?", entity_df.columns[::-1]
        )
        with st.expander("Edit entities"):
            entity_df = show_table(entity_df)
        return {"entities_df": entity_df, "label_column": label_column}
    else:
        st.info(f"Upload entity csv above to start editing")
        return None


def feature_configs():
    st.header("Prepare Features")
    feature_df = upload_csv("features", _validate_features)
    if feature_df is not None:
        column_config = {
            "type": st.column_config.SelectboxColumn(
                options=["categorical", "numerical", "boolean"]
            ),
            "category": st.column_config.SelectboxColumn(options=feature_df["category"].unique()),
        }
        with st.expander("Edit features"):
            result_df = show_table(feature_df, key=f"feature_editor", column_config=column_config)
        return {"features_df": result_df}
    else:
        st.info(f"Upload a feature csv above to start editing")
        return None


def explainer_configs():
    st.header("Prepare Explainer")
    explainer_file = st.file_uploader(f"Upload pickled RealApp", type="pkl")
    if explainer_file is not None:
        try:
            explainer = pickle.load(explainer_file)
        except Exception as e:
            st.error(f"Error unpickling explainer: {e}")
            return None
        if type(explainer) is not RealApp:
            st.error(f"Must provide pickled RealApp")
            return None
        return {"explainer": explainer}


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists("config.yml"):
        with open("context_config.yml", "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    loader.default_flow_style = False
    # Remove all empty strings from config_data
    for key, value in config_data.items():
        if isinstance(value, dict):
            for key2, value2 in value.items():
                if value2 == "":
                    config_data[key][key2] = None
        if value == "":
            config_data[key] = None
    existing_config.update(config_data)

    with open("context_config.yml", "w") as yaml_file:
        loader.dump(existing_config, yaml_file)


def context_configs():
    st.header("Configure Context")
    loader = yaml.YAML()

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
        show_probs = st.radio(
            "Does your model support probability outputs?", ["Yes", "No"], horizontal=True
        )
        config_data["show_probs"] = True if show_probs == "Yes" else False
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

    with st.expander("Select here to modify terms"):
        terms = [
            ("Entity", "What is being predicted on (Patient, House, Region, ...)"),
            ("Feature", "How to refer to information (Feature, Factor, Property, Variable, ...)"),
            ("Prediction", "Output of model (Price, Score, Probability, ...)"),
            ("Positive", "Features that increase the model output (Beneficial, Protective, ...)"),
            (
                "Negative",
                "Features that decrease the model output (Detrimental, Risk, Harmful ...)",
            ),
        ]
        config_data["terms"] = dict()
        for term, helper in terms:
            config_data["terms"][term.lower()] = st.text_input(
                term, max_chars=15, placeholder=helper
            )

    col1, col2 = st.columns(2)
    with col1:
        st.write("Select pages to enable:")
        all_pages = [
            "Explore a Prediction",
            "Similar Entities",
            "Compare Entities",
            "Experiment with Changes",
            "Understand the Model",
            "Settings",
        ]
        show_pages_bools = []
        for page in all_pages:
            show_pages_bools.append(st.toggle(page, value=True))
        config_data["pages_to_show"] = [
            page for page, show in zip(all_pages, show_pages_bools) if show
        ]
    with col2:
        allow_page_selection = st.radio(
            "Should users be able to enable additional pages?",
            ["Yes", "No"],
            horizontal=True,
            index=1,
        )
        config_data["allow_page_selection"] = True if allow_page_selection == "Yes" else False

    return {"context": config_data}


def run_components(components):
    results = {}
    for title in components:
        result = components[title]()
        st.divider()
        if result is None:
            return None
        else:
            results.update(result)
    return results


def new_database():
    database_name = st.text_input("Database name?", max_chars=15)
    if database_name is not None and database_name != "":
        results = run_components({
            "Entities": entity_configs,
            "Features": feature_configs,
            "Explainer": explainer_configs,
            "Context": context_configs,
        })
        if results is not None:
            drop_old = st.checkbox("Drop old database if exists?")
            if st.button("Prepare Database"):
                try:
                    pbar = st.progress(0)
                    db.prepare_database(
                        database_name,
                        entities_df=results["entities_df"],
                        features_df=results["features_df"],
                        realapp=results["explainer"],
                        context_dict=results["context"],
                        label_column=results["label_column"],
                        drop_old=drop_old,
                        streamlit_progress_bar_func=pbar.progress,
                        fit_explainers=False,
                    )
                except Exception as e:
                    st.error(f"Error preparing database: {e}")
                else:
                    st.success("Database prepared successfully!")
                    st.balloons()


def existing_database():
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "database_name" not in st.session_state:
        st.session_state.database_name = None
    if not st.session_state.connected:
        st.text_input("Database name?", max_chars=15, key="database_name")
        if st.session_state["database_name"] is not None:
            if st.button("Connect to database"):
                try:
                    db.connect_to_db(st.session_state["database_name"], drop_old=False)
                except Exception as e:
                    st.error(f"Error connecting to database {e}")
                else:
                    st.session_state.connected = True
                    st.rerun()
    else:
        st.info(f"Connected to {st.session_state.database_name}")
        if st.button("Disconnect"):
            db.disconnect_from_db()
            st.session_state.connected = False
            st.session_state.database_name = None
            st.rerun()
        entities = db.get_entities_df()
        st.data_editor(entities, key="entities")


def main():
    st.title("Configuration Wizard")
    setup_mode = st.radio("Setup mode", ["New Database", "Existing Database"], horizontal=True)
    if setup_mode == "New Database":
        new_database()
    if setup_mode == "Existing Database":
        existing_database()


if __name__ == "__main__":
    main()
