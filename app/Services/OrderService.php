<?php

namespace App\Services;

use App\Jobs\ProcessOrderJob;
use App\Models\Order;
use Illuminate\Support\Facades\Log;

class OrderService
{
    public function create(array $data): Order
    {
        $order = Order::create([
            'customer_name' => $data['customer_name'],
            'customer_email' => $data['customer_email'],
            'total_amount' => $data['total_amount'],
            'description' => $data['description'] ?? null,
            'status' => 'pending',
        ]);

        ProcessOrderJob::dispatch($order->id);

        return $order;
    }

    public function process(int $orderId): void
    {
        $order = Order::findOrFail($orderId);

        try {
            $externalApi = app(ExternalApiService::class);

            $externalData = $externalApi->getExternalData();

            $order->update([
                'status' => 'processed',
                'external_data' => $externalData,
                'error_message' => null,
            ]);
        } catch (\Throwable $e) {

            Log::error('Order processing failed', [
                'order_id' => $order->id,
                'customer_email' => $order->customer_email,
                'error' => $e->getMessage(),
            ]);

            $order->update([
                'status' => 'failed',
                'error_message' => $e->getMessage(),
            ]);
        }
    }
}
