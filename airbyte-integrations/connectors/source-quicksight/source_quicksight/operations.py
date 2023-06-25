import json
import boto3
import os.path
from pprint import pprint
from functools import partial

def _client_factory(config):
    aws_access_key_id = config["aws_access_key_id"]
    aws_secret_access_key = config["aws_secret_access_key"]
    region = config["aws_region_name"]
    client = boto3.client(
        "quicksight",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    return client

def _paginator_adaptor(client, operation_name, account_id, **kwargs):
    paginator = client.get_paginator(operation_name)
    wrapped = partial(paginator.paginate, AwsAccountId=account_id, **kwargs)
    return wrapped

def _client_adaptor(client, operation_name, account_id, **kwargs):
    if client.can_paginate(operation_name):
        pg = _paginator_adaptor(client, operation_name, account_id, **kwargs)
        dataset = [x for x in pg()]
        return dataset
    else:
        target = getattr(client, operation_name)
        data = target(AwsAccountId=account_id, **kwargs)
        return [data]

def _api_call(client, account_id, operation, foreign_key_name=None, envelope_name=None, parent=None):
    if (foreign_key_name is not None) and (parent is not None):
        parent_data = parent(client, account_id)
        results = []
        for page in parent_data:
            for item in page[envelope_name]:
                # ---------------------weird hack---------------------------
                # NOTE: small hack because the list_groups operation doesn't
                #       follow the same convention as the others.
                if operation == "list_groups":
                    fk = item["Name"]
                else:
                    fk = item[foreign_key_name]
                if operation == "list_groups":
                    kwargs = {"Namespace": fk}
                else:
                    kwargs = {foreign_key_name: fk}
                # ---------------------weird hack---------------------------
                fk = item[foreign_key_name]
                data = _client_adaptor(client, operation, account_id, **kwargs)
                for page in data:
                    results.append(page)
        
        return results
    else:
        data = _client_adaptor(client, operation, account_id)
        return data

operations = [
    ("list_dashboards", None),
    ("list_data_sets", None),
    ("list_data_sources", None),
    ("list_folders", None),
    ("list_namespaces", None),
    ("list_template", None),
    ("list_themes", None)
]

def list_dashboards(client, account_id):
    return _api_call(client, account_id, "list_dashboards")

def list_analyses(client, account_id):
    return _api_call(client, account_id, "list_analyses")

def list_data_sets(client, account_id):
    return _api_call(client, account_id, "list_data_sets")

def list_data_sources(client, account_id):
    return _api_call(client, account_id, "list_data_sources")

def list_folders(client, account_id):
    return _api_call(client, account_id, "list_folders")

def list_namespaces(client, account_id):
    return _api_call(client, account_id, "list_namespaces")

def list_templates(client, account_id):
    return _api_call(client, account_id, "list_templates")

def list_themes(client, account_id):
    return _api_call(client, account_id, "list_themes")

def list_dashboard_versions(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_dashboard_versions",
        envelope_name="DashboardSummaryList",
        foreign_key_name="DashboardId",
        parent=list_dashboards
    )

def list_ingestions(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_ingestions",
        envelope_name="DataSetSummaries",
        foreign_key_name="DataSetId",
        parent=list_data_sets
    )

def list_folder_members(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_folder_members",
        envelope_name="FolderSummaryList",
        foreign_key_name="FolderId",
        parent=list_folders
    )

def list_groups(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_groups",
        envelope_name="Namespaces",
        foreign_key_name="Namespace",
        parent=list_namespaces
    )

def list_template_aliases(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_template_aliases",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def list_template_versions(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_template_versions",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def list_theme_aliases(client, account_id):
    # NOTE: CLASSIC, and MIDNIGHT raise ResourceNotFoundException
    #       Handle later.
    return _api_call(
        client,
        account_id,
        "list_theme_aliases",
        envelope_name="ThemeSummaryList",
        foreign_key_name="ThemeId",
        parent=list_themes
    )

def list_theme_versions(client, account_id):
    return _api_call(
        client,
        account_id,
        "list_theme_versions",
        envelope_name="ThemeSummaryList",
        foreign_key_name="ThemeId",
        parent=list_themes
    )

def describe_account_settings(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_account_settings"
    )

def describe_account_subscription(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_account_subscription"
    )

def describe_analysis(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_analysis",
        envelope_name="AnalysisSummaryList",
        foreign_key_name="AnalysisId",
        parent=list_analyses
    )

def describe_analysis_definition(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_analysis_definition",
        envelope_name="AnalysisSummaryList",
        foreign_key_name="AnalysisId",
        parent=list_analyses
    )

def describe_analysis_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_analysis_permissions",
        envelope_name="AnalysisSummaryList",
        foreign_key_name="AnalysisId",
        parent=list_analyses
    )

def describe_dashboards(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_dashboard",
        envelope_name="DashboardSummaryList",
        foreign_key_name="DashboardId",
        parent=list_dashboards
    )

def describe_dashboard_definition(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_dashboard",
        envelope_name="DashboardSummaryList",
        foreign_key_name="DashboardId",
        parent=list_dashboards
    )

def describe_dashboard_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_dashboard_permissions",
        envelope_name="DashboardSummaryList",
        foreign_key_name="DashboardId",
        parent=list_dashboards
    )



if __name__ == "__main__":
    with open("secrets/config.json") as F:
        config = json.loads(F.read())

    client = _client_factory(config)
    account_id = config["aws_account_id"]
    print("starting...")
    # pprint(list_dashboards(client, account_id))
    # pprint(list_dashboard_versions(client, account_id))
    pprint(list_analyses(client, account_id))
    # pprint(list_data_sets(client, account_id))
    # import pdb
    # pdb.set_trace()
    # pprint(list_ingestions(client, account_id))
    # pprint(list_folder_members(client, account_id))
    # pprint(list_data_sources(client, account_id))
    # pprint(list_folders(client, account_id))
    # pprint(list_namespaces(client, account_id))
    # pprint(list_themes(client, account_id))
    # pprint(list_theme_aliases(client, account_id))            # The two theme functions throw errors
    # pprint(list_theme_versions(client, account_id))
    # pprint(list_templates(client, account_id))
    # pprint(list_template_aliases(client, account_id))
    # pprint(list_template_versions(client, account_id))
    # pprint(list_groups(client, account_id))                   # borked! call the sysadmin!
    # pprint(describe_account_settings(client, account_id))
    # pprint(describe_account_subscription(client, account_id))
    # pprint(describe_analysis(client, account_id))
    # pprint(describe_analysis_definition(client, account_id))
    # pprint(describe_analysis_permissions(client, account_id))
    # pprint(describe_dashboards(client, account_id))
    # pprint(describe_dashboard_definition(client, account_id))
    pprint(describe_dashboard_permissions(client, account_id))
    pprint("finished!")
