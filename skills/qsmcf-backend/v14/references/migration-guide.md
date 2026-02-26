# Migration Guide

Database migrations using Laravel Schema Builder in QSCMF v14.

## Create Migration

```bash
php artisan make:migration create_product_table
```

## Migration Structure

```php
<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateProductTable extends Migration
{
    public function up()
    {
        Schema::create('product', function (Blueprint $table) {
            $table->id();
            $table->string('product_name', 200);
            $table->integer('status')->default(1);
            $table->integer('create_time')->nullable();
        });
    }

    public function down()
    {
        Schema::dropIfExists('product');
    }
}
```

## Run Migration

```bash
php artisan migrate
php artisan migrate:rollback
```

---

## Related Documentation
- [Migration Metadata](migration-metadata.md)
- [Model Guide](model-guide.md)
