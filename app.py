from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SynonymMap,
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
)


class SynonymMapManager:
    # ---- Configuration ----
    _search_service_endpoint = "https://<YOUR-SEARCH-SERVICE-NAME>.search.windows.net"
    _api_key = "<YOUR-ADMIN-API-KEY>"

    _credential = AzureKeyCredential(_api_key)

    # Index client (used also for synonym maps)
    _index_client = SearchIndexClient(
        endpoint=_search_service_endpoint,
        credential=_credential,
    )

    # -------------------------------------------------------------------------
    # Synonym map CRUD
    # -------------------------------------------------------------------------
    def create_or_update_synonym_map(self, name: str, synonyms: List[str]) -> SynonymMap:
        """Create or update a synonym map."""
        synonym_map = SynonymMap(
            name=name,
            format="solr",
            synonyms=synonyms,
        )
        return self._index_client.create_or_update_synonym_map(synonym_map)

    def get_synonym_map(self, name: str) -> SynonymMap:
        """Retrieve a synonym map by name."""
        return self._index_client.get_synonym_map(name)

    def list_synonym_maps(self):
        """List all synonym maps in the search service."""
        return self._index_client.list_synonym_maps()

    def delete_synonym_map(self, name: str):
        """Delete a synonym map by name."""
        self._index_client.delete_synonym_map(name)

    def synonym_map_exists(self, name: str) -> bool:
        """Check if a synonym map exists by name."""
        try:
            self._index_client.get_synonym_map(name)
            return True
        except ResourceNotFoundError:
            return False

    # -------------------------------------------------------------------------
    # Assign synonym maps to fields
    # -------------------------------------------------------------------------
    def assign_synonym_map_to_all_fields(self, index_name: str, synonym_map_name: str):
        """
        Assign a synonym map to all eligible fields in an existing index.

        Rules:
        - Only searchable fields
        - Only string (Edm.String) fields
        - Not the key field
        - Must not already have a synonym map
        """
        index = self._index_client.get_index(index_name)
        updated = False

        for field in index.fields:
            # 1) Must be searchable
            if not getattr(field, "searchable", False):
                print(
                    f"Field '{field.name}' is not searchable. "
                    "Synonym maps only work on searchable string fields."
                )
                continue

            # 2) Must be string
            if field.type != SearchFieldDataType.String:
                print(
                    f"Field '{field.name}' is not a string field. "
                    "Synonym maps only work on Edm.String types."
                )
                continue

            # 3) Must not be the key field
            if getattr(field, "key", False):
                print(
                    f"Field '{field.name}' is the key field. "
                    "A synonym map cannot be assigned to a key field."
                )
                continue

            # 4) Must not already have a synonym map
            existing = getattr(field, "synonym_map_names", None)
            if existing:
                print(
                    f"Field '{field.name}' already has a synonym map: {existing}. "
                    "Remove it before assigning a new one."
                )
                continue

            # Assign map
            field.synonym_map_names = [synonym_map_name]
            updated = True
            print(
                f"✅ Assigned synonym map '{synonym_map_name}' to field '{field.name}' "
                f"in index '{index_name}'."
            )

        if updated:
            # Single update for the whole index (more efficient than per-field)
            self._index_client.create_or_update_index(index)
        else:
            print("No fields were updated. Either no eligible fields or all already had a synonym map.")

    def assign_synonym_map_to_field(self, index_name: str, field_name: str, synonym_map_name: str):
        """
        Assign a synonym map to a specific field in an existing index.

        Rules:
        - Only searchable fields
        - Only string (Edm.String) fields
        - Not the key field
        - Must not already have a synonym map
        """
        index = self._index_client.get_index(index_name)
        target_field = None

        for field in index.fields:
            if field.name == field_name:
                target_field = field
                break

        if target_field is None:
            raise ValueError(f"Field '{field_name}' does not exist in index '{index_name}'.")

        # 1) Must be searchable
        if not getattr(target_field, "searchable", False):
            raise ValueError(
                f"Field '{field_name}' is not searchable. "
                "Synonym maps only work on searchable string fields."
            )

        # 2) Must be string
        if target_field.type != SearchFieldDataType.String:
            raise ValueError(
                f"Field '{field_name}' is not a string field. "
                "Synonym maps only work on Edm.String types."
            )

        # 3) Must not be the key field
        if getattr(target_field, "key", False):
            raise ValueError(
                f"Field '{field_name}' is the key field. "
                "A synonym map cannot be assigned to a key field."
            )

        # 4) Must not already have a synonym map
        existing = getattr(target_field, "synonym_map_names", None)
        if existing:
            raise ValueError(
                f"Field '{field_name}' already has a synonym map: {existing}. "
                "Remove it before assigning a new one."
            )

        # Assign and update
        target_field.synonym_map_names = [synonym_map_name]
        self._index_client.create_or_update_index(index)

        print(
            f"✅ Synonym map '{synonym_map_name}' assigned to field '{field_name}' "
            f"in index '{index_name}'."
        )

    # -------------------------------------------------------------------------
    # Index creation + inspection
    # -------------------------------------------------------------------------
    def create_index(self, index_name: str):
        """Create or update a demo index with a few fields."""
        fields = [
            # Key field (must be a SimpleField with key=True)
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=False,
                sortable=False,
                facetable=False,
            ),
            # Title: searchable, filterable, sortable
            SearchableField(
                name="title",
                type=SearchFieldDataType.String,
                sortable=True,
                filterable=True,
                facetable=False,
            ),
            # Content: main text, searchable, synonym-enabled later
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=False,
                facetable=False,
            ),
            # Category: simple filterable field
            SimpleField(
                name="category",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            # Tags: a collection of strings, searchable + facetable
            SearchableField(
                name="tags",
                collection=True,
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            # Created date: useful for sorting/filtering
            SimpleField(
                name="created_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
                facetable=False,
            ),
        ]

        index = SearchIndex(
            name=index_name,
            fields=fields,
        )

        self._index_client.create_or_update_index(index)
        print(f"✅ Index '{index_name}' created or updated.")

    def list_fields_with_synonym_maps(self, index_name: str):
        """Print all fields that have synonym maps assigned."""
        index = self._index_client.get_index(index_name)

        print(f"\nSynonym map assignments in index '{index_name}':\n")
        found_any = False

        for field in index.fields:
            synonym_maps = getattr(field, "synonym_map_names", None)
            if synonym_maps:
                found_any = True
                print(f"🟦 Field: {field.name}")
                print(f"     Synonym maps: {synonym_maps}")

        if not found_any:
            print("⚠️ No fields in this index have synonym maps assigned.")


if __name__ == "__main__":
    manager = SynonymMapManager()
    index_name = "demo-tech-index"

    manager.create_index(index_name)

    # Example synonym map
    synonym_map_name = "tech-synonyms-equivalency"
    synonyms = [
        'ui, "user interface", frontend',
        'ux, "user experience"',
        'aks, "azure kubernetes service", kubernetes',
        'iaas, "infrastructure as a service"',
        'api, "application programming interface"',
        'sql, "structured query language"',
        'vm, "virtual machine"',
        'gpu, "graphics processing unit"',
        'cpu, "central processing unit"',
        "repo, repository",
        'ide, "integrated development environment"',
        'devops, "development operations"',
    ]

    # 1) Check if the synonym map exists; if not, create it
    if manager.synonym_map_exists(synonym_map_name):
        print(f"Synonym map '{synonym_map_name}' already exists.")
    else:
        print(f"Synonym map '{synonym_map_name}' does not exist, creating it...")
        synonym_map = manager.create_or_update_synonym_map(synonym_map_name, synonyms)
        print(f"Synonym map '{synonym_map_name}' created with {len(synonym_map.synonyms)} rules.")

    # 2) Retrieve and print the synonym map
    synonym_map = manager.get_synonym_map(synonym_map_name)
    print(f"\nRetrieved synonym map '{synonym_map_name}':")
    for rule in synonym_map.synonyms:
        print("  ", rule)

    # 3) Show fields with synonym maps before and after assignment
    print("\n--- BEFORE ASSIGNMENT ---")
    manager.list_fields_with_synonym_maps(index_name)

    print("\nAssigning synonym map to all eligible fields...")
    manager.assign_synonym_map_to_all_fields(index_name, synonym_map_name)

    print("\n--- AFTER ASSIGNMENT ---")
    manager.list_fields_with_synonym_maps(index_name)
