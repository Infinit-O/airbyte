import json
import boto3
import logging
from time import sleep, time
from pprint import pprint
from functools import partial

logs = logging.getLogger('airbyte')

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
    logs.info(f"working on operation -> {operation}")
    if (foreign_key_name is not None) and (parent is not None):
        parent_data = parent(client, account_id)
        results = []
        for page in parent_data:
            for item in page[envelope_name]:
                # ---------------------weird hack---------------------------
                # NOTE: small hack because the list_groups operation doesn't
                #       follow the same convention as the others.
                if operation in ["list_groups", "describe_namespace"]:
                    fk = item["Name"]
                else:
                    fk = item[foreign_key_name]
                if operation in ["list_groups", "describe_namespace"]:
                    kwargs = {"Namespace": fk}
                else:
                    kwargs = {foreign_key_name: fk}
                # ---------------------weird hack---------------------------

                fk = item[foreign_key_name]
                # ---------------------weird hack 2---------------------------
                # NOTE: certain data sets are not available via API access,
                #       and are not needed. 
                if operation == "describe_data_set":
                    try:
                        data = _client_adaptor(client, operation, account_id, **kwargs)
                    except:
                        continue
                else: 
                    data = _client_adaptor(client, operation, account_id, **kwargs)
                # ---------------------weird hack 2---------------------------

                for page in data:
                    results.append(page)
                sleep(5)
        return results
    else:
        data = _client_adaptor(client, operation, account_id)
        return data


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

def describe_data_set(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_data_set",
        envelope_name="DataSetSummaries",
        foreign_key_name="DataSetId",
        parent=list_data_sets
    )

def describe_data_set_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_data_set_permissions",
        envelope_name="DataSetSummaries",
        foreign_key_name="DataSetId",
        parent=list_data_sets
    )

def describe_data_source(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_data_source",
        envelope_name="DataSources",
        foreign_key_name="DataSourceId",
        parent=list_data_sources
    )

def describe_data_source_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_data_source_permissions",
        envelope_name="DataSources",
        foreign_key_name="DataSourceId",
        parent=list_data_sources
    )

def describe_folders(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_folder",
        envelope_name="FolderSummaryList",
        foreign_key_name="FolderId",
        parent=list_folders
    )

def describe_folder_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_folder_permissions",
        envelope_name="FolderSummaryList",
        foreign_key_name="FolderId",
        parent=list_folders
    )

def describe_folder_resolved_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_folder_resolved_permissions",
        envelope_name="FolderSummaryList",
        foreign_key_name="FolderId",
        parent=list_folders
    )

def describe_group(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_group",
        envelope_name="GroupSummaryList",
        foreign_key_name="GroupId",
        parent=list_groups
    )

def describe_group_membership(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_group_membership",
        envelope_name="GroupeSummaryList",
        foreign_key_name="GroupId",
        parent=list_groups
    )

# NOTE: requires dataset id AND ingestion id! special case!
def describe_ingestions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_ingestion",
        envelope_name="Ingestions",
        foreign_key_name="IngestionId",
        parent=list_ingestions
    )

def describe_ip_restriction(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_ip_restriction"
    )

def describe_namespace(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_namespace",
        envelope_name="Namespaces",
        foreign_key_name="Name",
        parent=list_namespaces
    )

def describe_template(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_template",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def describe_template_alias(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_template",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def describe_template_definition(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_template",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def describe_template_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_template",
        envelope_name="TemplateSummaryList",
        foreign_key_name="TemplateId",
        parent=list_templates
    )

def describe_theme(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_theme",
        envelope_name="ThemeSummaryList",
        foreign_key_name="ThemeId",
        parent=list_themes
    )

def describe_theme_alias(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_theme_alias",
        envelope_name="ThemeSummaryList",
        foreign_key_name="ThemeId",
        parent=list_themes
    )

def describe_theme_permissions(client, account_id):
    return _api_call(
        client,
        account_id,
        "describe_theme_permissions",
        envelope_name="ThemeSummaryList",
        foreign_key_name="ThemeId",
        parent=list_themes
    )

def describe_user(client, account_id):
    return None

def describe_iam_policy_assignment(client, account_id):
    return _api_call()

op_map_dict = {
    "list_dashboards": list_dashboards,
    "list_dashboard_versions": list_dashboard_versions,
    "list_analyses": list_analyses,
    "list_data_sets": list_data_sets,
    "list_ingestions": list_ingestions,
    "list_data_sources": list_data_sources,
    "list_folders": list_folders,
    "list_folder_members": list_folder_members,
    "list_namespaces": list_namespaces,
    # "list_users": list_users,
    # "list_iam_policy_assignments_for_user": list_iam_policy_assignments_for_user,
    # "list_user_groups": list_user_groups,
    # "list_groups": list_groups,
    # "list_group_memberships": list_group_memberships,
    # "list_iam_policy_assignments": list_iam_policy_assignments,
    "list_templates": list_templates,
    "list_template_aliases": list_template_aliases,
    "list_template_versions": list_template_versions,
    "list_themes": list_themes,
    # "describe_themes": describe_themes,
    # "list_theme_aliases": list_theme_aliases,
    # "list_theme_versions": list_theme_versions,
    # "describe_account_customization": describe_account_customization # this does not exist 
    "describe_account_settings": describe_account_settings,
    "describe_account_subscription": describe_account_subscription,
    "describe_analysis": describe_analysis,
    "describe_analysis_definition": describe_analysis_definition,
    "describe_analysis_permissions": describe_analysis_permissions,
    "describe_dashboard": describe_dashboards,
    "describe_dashboard_definition": describe_dashboard_definition,
    "describe_dashboard_permissions": describe_dashboard_permissions,
    "describe_data_set": describe_data_set,
    "describe_data_set_permissions": describe_data_set_permissions,
    "describe_data_source": describe_data_source,
    "describe_data_source_permissions": describe_data_source_permissions,
    "describe_folder": describe_folders,
    "describe_folder_permissions": describe_folder_permissions,
    "describe_folder_resolved_permissions": describe_folder_resolved_permissions,
    # "describe_group": describe_group,
    # "describe_group_membership": describe_group_membership,
    # "describe_iam_policy_assignment": describe_iam_policy_assignment,
    # "describe_ingestion": describe_ingestions,
    # "describe_ip_restrictions": describe_ip_restriction,
    # "describe_namespace": describe_namespace,
    "describe_template": describe_template,
    "describe_template_alias": describe_template_alias,
    "describe_template_definition": describe_template_definition,
    "describe_template_permissions": describe_template_permissions,
    # "describe_theme": describe_theme,
    # "describe_theme_alias": describe_theme_alias,
    # "describe_theme_permissions": describe_theme_permissions,
    # "describe_user": describe_user
}

# if __name__ == "__main__":
#     # This whole section is for manual testing pls ignore it, ty
#     with open("secrets/config.json") as F:
#         config = json.loads(F.read())

#     client = _client_factory(config)
#     account_id = config["aws_account_id"]
#     starttime = time()
#     print("starting...")
#     for k, v in op_map_dict.items():
#         print(f"{k} -> {v}")
#         v(client, account_id)
#     endtime = time()
#     duration = endtime - starttime
#     pprint(f"finished! operation took {duration} seconds")
