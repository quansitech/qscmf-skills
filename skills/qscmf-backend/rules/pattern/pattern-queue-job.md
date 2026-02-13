# Queue Job Pattern

## When to Use

For time-consuming tasks (image processing, email sending, API calls), use queue jobs to avoid blocking the main request.

## Architecture

```
Controller
    ↓
  Queue::push
    ↓
  Job (stored in Redis)
    ↓
Worker (background process)
    ↓
  Job Handler
```

## Create Job

```php
namespace Common\Job;
use Think\Queue\Job;

/**
 * Image processing job
 */
class ProcessImageJob
{
    protected $data;

    public function __construct(array $data)
    {
        $this->data = $data;
    }

    /**
     * Execute the job
     */
    public function handle(Job $job, array $data)
    {
        try {
            $imageId = $data['image_id'];
            $operations = $data['operations'] ?? [];

            // Process image
            $image = D('Image')->find($imageId);

            foreach ($operations as $operation) {
                switch ($operation['type']) {
                    case 'resize':
                        $this->resizeImage($image, $operation);
                        break;
                    case 'thumbnail':
                        $this->createThumbnail($image, $operation);
                        break;
                }
            }

            // Mark as processed
            D('Image')->where(['id' => $imageId])->save([
                'status' => 1,
                'processed_at' => time()
            ]);

            $job->delete();
            return true;

        } catch (\Exception $e) {
            // Release job for retry
            if ($job->attempts() < 3) {
                $job->release(60); // Retry after 60 seconds
            } else {
                $job->failed(); // Max retries reached
            }
            return false;
        }
    }

    protected function resizeImage(array $image, array $operation): void
    {
        // Resize logic
    }

    protected function createThumbnail(array $image, array $operation): void
    {
        // Thumbnail logic
    }
}
```

## Dispatch Job from Controller

```php
namespace Admin\Controller;
use Admin\Controller\QsListController;

class ImageController extends QsListController
{
    /**
     * Upload and queue processing
     */
    public function upload()
    {
        $file = $_FILES['file'];

        // Save to database
        $imageId = D('Image')->add([
            'filename' => $file['name'],
            'filepath' => $uploadPath,
            'status' => 0, // Pending
            'created_at' => time()
        ]);

        // Queue processing job
        \Think\Queue::push(new \Common\Job\ProcessImageJob([
            'image_id' => $imageId,
            'operations' => [
                ['type' => 'resize', 'width' => 800, 'height' => 600],
                ['type' => 'thumbnail', 'width' => 200, 'height' => 200]
            ]
        ]));

        $this->success('上传成功，正在处理中...');
    }
}
```

## Start Queue Worker

```bash
# Development
QUEUE_ENV=dev QUEUE_COUNT=1 php app/queue_resque.php

# Production (multiple workers)
QUEUE_ENV=prod QUEUE_COUNT=3 php app/queue_resque.php
```

## Supervisor Configuration

```ini
# /etc/supervisor/conf.d/qscmf-queue.conf

[program:qscmf-queue]
command=php /path/to/qscmf/app/queue_resque.php
process_name=%(program_name)s_%(process_num)02d
directory=/path/to/qscmf
numprocs=3
autostart=true
autorestart=true
user=www-data
redirect_stderr=true
stdout_logfile=/var/log/qscmf-queue.log
environment=QUEUE_ENV="prod",QUEUE_COUNT="1"
```

## Failed Job Handling

```php
/**
 * Failed job handler
 */
public function failed(Job $job, \Exception $e): void
{
    // Log error
    \Think\Log::record('Job failed: ' . $e->getMessage(), 'error');

    // Notify admin
    D('AdminNotification')->add([
        'type' => 'job_failed',
        'message' => $e->getMessage(),
        'job_data' => json_encode($this->data)
    ]);
}
```

→ [Admin Controllers Guide](references/admin-controllers.md)
