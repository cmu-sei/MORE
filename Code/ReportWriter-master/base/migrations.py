from django.db import migrations
from django.db.transaction import atomic


class DifferentAppMigration(migrations.Migration):
    """
        This is a custom migration that allows an application to modify the model of another
        app and host the migration files of that change.
    """
    migrated_app = None

    def __init__(self, name, app_label):
        super(DifferentAppMigration, self).__init__(name, app_label)
        if self.migrated_app is None:
            self.migrated_app = self.app_label

    def mutate_state(self, project_state, preserve=True):
        """
        Takes a ProjectState and returns a new one with the migration's
        operations applied to it. Preserves the original object state by
        default and will return a mutated state from a copy.
        """
        new_state = project_state
        if preserve:
            new_state = project_state.clone()

        for operation in self.operations:
            operation.state_forwards(self.migrated_app, new_state)
        return new_state

    def apply(self, project_state, schema_editor, collect_sql=False):
        """
        Takes a project_state representing all migrations prior to this one
        and a schema_editor for a live database and applies the migration
        in a forwards order.

        Returns the resulting project state for efficient re-use by following
        Migrations.
        """
        for operation in self.operations:
            # If this operation cannot be represented as SQL, place a comment
            # there instead
            if collect_sql and not operation.reduces_to_sql:
                schema_editor.collected_sql.append("--")
                schema_editor.collected_sql.append("-- MIGRATION NOW PERFORMS OPERATION THAT CANNOT BE "
                                                   "WRITTEN AS SQL:")
                schema_editor.collected_sql.append("-- %s" % operation.describe())
                schema_editor.collected_sql.append("--")
                continue
            # Save the state before the operation has run
            old_state = project_state.clone()
            operation.state_forwards(self.migrated_app, project_state)
            # Run the operation
            if not schema_editor.connection.features.can_rollback_ddl and operation.atomic:
                # We're forcing a transaction on a non-transactional-DDL backend
                with atomic(schema_editor.connection.alias):
                    operation.database_forwards(self.migrated_app, schema_editor, old_state, project_state)
            else:
                # Normal behaviour
                operation.database_forwards(self.migrated_app, schema_editor, old_state, project_state)
        return project_state

    def unapply(self, project_state, schema_editor, collect_sql=False):
        """
        Takes a project_state representing all migrations prior to this one
        and a schema_editor for a live database and applies the migration
        in a reverse order.

        The backwards migration process consists of two phases:

        1. The intermediate states from right before the first until right
           after the last operation inside this migration are preserved.
        2. The operations are applied in reverse order using the states
           recorded in step 1.
        """
        # Construct all the intermediate states we need for a reverse migration
        to_run = []
        new_state = project_state
        # Phase 1
        for operation in self.operations:
            # If it's irreversible, error out
            if not operation.reversible:
                raise DifferentAppMigration.IrreversibleError("Operation %s in %s is not reversible" % (operation, self))
            # Preserve new state from previous run to not tamper the same state
            # over all operations
            new_state = new_state.clone()
            old_state = new_state.clone()
            operation.state_forwards(self.migrated_app, new_state)
            to_run.insert(0, (operation, old_state, new_state))

        # Phase 2
        for operation, to_state, from_state in to_run:
            if collect_sql:
                if not operation.reduces_to_sql:
                    schema_editor.collected_sql.append("--")
                    schema_editor.collected_sql.append("-- MIGRATION NOW PERFORMS OPERATION THAT CANNOT BE "
                                                       "WRITTEN AS SQL:")
                    schema_editor.collected_sql.append("-- %s" % operation.describe())
                    schema_editor.collected_sql.append("--")
                    continue
            if not schema_editor.connection.features.can_rollback_ddl and operation.atomic:
                # We're forcing a transaction on a non-transactional-DDL backend
                with atomic(schema_editor.connection.alias):
                    operation.database_backwards(self.migrated_app, schema_editor, from_state, to_state)
            else:
                # Normal behaviour
                operation.database_backwards(self.migrated_app, schema_editor, from_state, to_state)
        return project_state