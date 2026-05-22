import os
from django.core.files.base import ContentFile
from whitenoise.storage import CompressedStaticFilesStorage, CompressedManifestStaticFilesStorage
from jsmin import jsmin
from rcssmin import cssmin

class OptimizedStorageMixin:
    def post_process(self, paths, dry_run=False, **options):
        # Only process files when collecting (not dry run)
        for name, info in paths.items():
            if not dry_run and name.endswith('.css'):
                storage, path = info
                try:
                    with storage.open(path) as f:
                        content = f.read().decode('utf-8')
                    minified = cssmin(content)
                    storage.delete(path)
                    storage.save(path, ContentFile(minified.encode('utf-8')))
                except Exception as e:
                    print(f"Error minifying CSS {name}: {e}")
            elif not dry_run and name.endswith('.js'):
                storage, path = info
                try:
                    with storage.open(path) as f:
                        content = f.read().decode('utf-8')
                    minified = jsmin(content)
                    storage.delete(path)
                    storage.save(path, ContentFile(minified.encode('utf-8')))
                except Exception as e:
                    print(f"Error minifying JS {name}: {e}")

        # Delegate to parent storage backend to compress (gzip/brotli) and hash the minified files
        return super().post_process(paths, dry_run, **options)

class OptimizedStaticFilesStorage(OptimizedStorageMixin, CompressedStaticFilesStorage):
    pass

class OptimizedManifestStaticFilesStorage(OptimizedStorageMixin, CompressedManifestStaticFilesStorage):
    pass
