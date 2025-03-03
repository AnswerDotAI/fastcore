def __getattr__(name):
     raise ImportError(
         f"Could not import '{name}' from fastcore.transform - this module has been moved to the fasttransform package.\n"
         "To migrate your code, please see the migration guide at: https://answerdotai.github.io/fasttransform/fastcore_migration_guide.html"
     )