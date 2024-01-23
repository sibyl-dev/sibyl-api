import io
import os
import pickle

import pandas as pd
import ruamel.yaml as yaml
import streamlit as st
from pyreal import RealApp

from sibyl.db import preprocessing as db
from sibyl.utils import get_project_root


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


def upload_csv(term, validate_func, edit_mode=False):
    label = f"Upload {term} file"
    if edit_mode:
        label = f"Replace {term} file"
    csv = st.file_uploader(label, type="csv", key=f"{term}_file")
    df = None
    if csv is not None:
        df = pd.read_csv(csv)
        if not validate_func(df):
            return None
    return df


def entity_configs(default=None):
    st.header("Prepare Entities")
    entity_df = upload_csv("entities", _validate_entities, edit_mode=(default is not None))
    if entity_df is None and default is not None:
        entity_df = default
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


def feature_configs(default=None):
    st.header("Prepare Features")
    feature_df = upload_csv("features", _validate_features, edit_mode=(default is not None))
    if feature_df is None and default is not None:
        feature_df = default
    if feature_df is not None:
        column_config = {
            "type": st.column_config.SelectboxColumn(
                options=["categorical", "numerical", "boolean"]
            ),
            "category": st.column_config.SelectboxColumn(options=feature_df["category"].unique()),
            "values": st.column_config.ListColumn(),
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
    path = os.path.join(get_project_root(), "sibyl", "templates", "context_config_template.yml")
    if os.path.exists(path):
        with open(path, "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def download_config(loader, config_data, existing_config):
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

    stream = io.StringIO()
    loader.dump(existing_config, stream)
    stream.seek(0)
    st.download_button(label="Download config", data=stream.read(), file_name="context_config.yml")


def context_configs(config_dict=None):
    st.header("Configure Context")
    if config_dict is None:
        config_dict = {}

    config_data = dict()

    use_rows = st.radio(
        "Does your data have multiple rows?",
        ["No", "Yes"],
        horizontal=True,
        index=(1 if config_dict.get("use_rows", False) else 0),
    )
    config_data["use_rows"] = True if use_rows == "Yes" else False

    if config_data["use_rows"]:
        config_data["row_label"] = st.text_input(
            "How should we label rows?", max_chars=25, value=config_dict.get("row_label", "")
        )

    output_type = st.radio(
        "What is your model's output type?",
        ["Numeric", "Boolean", "Categorical"],
        horizontal=True,
        index=(
            0
            if config_dict.get("output_type", "numeric") == "numeric"
            else 1 if config_dict.get("output_type", "numeric") == "boolean" else 2
        ),
    )
    config_data["output_type"] = output_type.lower()

    if config_data["output_type"] == "boolean":
        show_probs = st.radio(
            "Does your model support probability outputs?",
            ["No", "Yes"],
            horizontal=True,
            index=(1 if config_dict.get("show_probs", False) else 0),
        )
        config_data["show_probs"] = True if show_probs == "Yes" else False
        config_data["output_pos_label"] = st.text_input(
            "How should we label predictions of 'True'?",
            max_chars=25,
            value=(config_dict.get("output_pos_label", "")),
        )
        config_data["output_neg_label"] = st.text_input(
            "How should we label predictions of 'False'?",
            max_chars=25,
            value=(config_dict.get("output_neg_label", "")),
        )
    if config_data["output_type"] == "numeric":
        output_format_string = st.radio(
            "How should we format the output?",
            ["1,234", "1,234.56", "$1,234", "$1,234.56", "No Formatting", "Custom"],
            horizontal=True,
            index=(0 if config_dict.get("output_format_string", None) is None else 5),
        )
        if output_format_string == "Custom":
            config_data["output_format_string"] = st.text_input(
                "How should we format the output (python f-string)?",
                value=config_dict.get("output_format_string", ""),
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
        index=(
            1
            if config_dict.get("output_sentiment_is_negative", None)
            else 2 if config_dict.get("output_sentiment_is_negative", None) is None else 0
        ),
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
            ("Positive", "Features that increase the model output (Beneficial, Detrimental, ...)"),
            (
                "Negative",
                "Features that decrease the model output (Beneficial, Detrimental, ...)",
            ),
        ]
        config_data["terms"] = dict()
        for term, helper in terms:
            config_data["terms"][term.lower()] = st.text_input(
                term,
                max_chars=15,
                placeholder=helper,
                value=config_dict.get("terms", {}).get(term.lower(), None),
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
            show_pages_bools.append(
                st.toggle(
                    page,
                    value=(True if page in config_dict.get("pages_to_show", all_pages) else False),
                )
            )
        config_data["pages_to_show"] = [
            page for page, show in zip(all_pages, show_pages_bools) if show
        ]
    with col2:
        allow_page_selection = st.radio(
            "Should users be able to enable additional pages?",
            ["No", "Yes"],
            horizontal=True,
            index=(1 if config_dict.get("allow_page_selection", True) else 0),
        )
        config_data["allow_page_selection"] = True if allow_page_selection == "Yes" else False

    loader = yaml.YAML()
    existing_config = load_existing_config(loader)
    download_config(loader, config_data, existing_config)

    return {"context": config_data}


def run_components(components):
    results = {}
    for component in components:
        default = None
        if len(component) == 2:
            title, func = component
        elif len(component) == 3:
            title, func, default = component
        else:
            raise ValueError("Expected 2 or 3 values in component tuple (title, func, default)")
        if default is not None:
            result = func(default)
        else:
            result = func()
        st.divider()
        if result is None:
            return None
        else:
            results.update(result)
    return results


def new_database():
    database_name = st.text_input("Database name?", max_chars=15)
    if database_name is not None and database_name != "":
        results = run_components([
            ("Entities", entity_configs),
            ("Features", feature_configs),
            ("Explainer", explainer_configs),
            ("Context", context_configs),
        ])
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
    if not st.session_state.connected:
        database_name = st.text_input("Database name?", max_chars=15)
        if database_name is not None:
            st.session_state["database_name"] = database_name
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
        results = run_components([
            ("Entities", entity_configs, db.get_entities_df()),
            ("Features", feature_configs, db.get_features_df()),
            ("Context", context_configs, db.get_context_dict()),
        ])
        if st.button("Prepare Database"):
            try:
                pbar = st.progress(0)
                db.prepare_database(
                    st.session_state["database_name"],
                    entities_df=results["entities_df"],
                    features_df=results["features_df"],
                    context_dict=results["context"],
                    label_column=results["label_column"],
                    drop_old=True,
                    streamlit_progress_bar_func=pbar.progress,
                    fit_explainers=False,
                )
            except Exception as e:
                st.error(f"Error preparing database: {e}")
            else:
                st.success("Database prepared successfully!")
                st.balloons()


def main():
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "database_name" not in st.session_state:
        st.session_state.database_name = None

    st.title("Configuration Wizard")
    setup_mode = st.radio("Setup mode", ["New Database", "Existing Database"], horizontal=True)
    if setup_mode == "New Database":
        new_database()
    if setup_mode == "Existing Database":
        existing_database()


if __name__ == "__main__":
    main()
