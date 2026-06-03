<?php

namespace Tests\Feature;

use App\Jobs\ProcessOrderJob;
use App\Models\Order;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Queue;
use Tests\TestCase;

class OrderApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_list_orders(): void
    {
        Order::factory()->count(3)->create();

        $response = $this->getJson('/api/orders');

        $response->assertOk()
            ->assertJsonCount(3, 'data');
    }

    public function test_can_create_order(): void
    {
        Queue::fake();

        $payload = [
            'customer_name' => 'Ricardo Saucedo',
            'customer_email' => 'ricardo@test.com',
            'total_amount' => 1500.50,
            'description' => 'Pedido de prueba',
        ];

        $response = $this->postJson('/api/orders', $payload);

        $response->assertCreated()
            ->assertJsonPath('message', 'Order created successfully')
            ->assertJsonPath('data.customer_name', 'Ricardo Saucedo')
            ->assertJsonPath('data.status', 'pending');

        $this->assertDatabaseHas('orders', [
            'customer_email' => 'ricardo@test.com',
            'status' => 'pending',
            'description' => 'Pedido de prueba',
        ]);

        Queue::assertPushed(ProcessOrderJob::class);
    }

    public function test_customer_name_is_required(): void
    {
        $response = $this->postJson('/api/orders', [
            'customer_email' => 'ricardo@test.com',
            'total_amount' => 1500,
        ]);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['customer_name']);
    }

    public function test_customer_email_must_be_valid(): void
    {
        $response = $this->postJson('/api/orders', [
            'customer_name' => 'Ricardo Saucedo',
            'customer_email' => 'not-an-email',
            'total_amount' => 1500,
        ]);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['customer_email']);
    }

    public function test_total_amount_must_be_at_least_one(): void
    {
        $response = $this->postJson('/api/orders', [
            'customer_name' => 'Ricardo Saucedo',
            'customer_email' => 'ricardo@test.com',
            'total_amount' => 0,
        ]);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['total_amount']);
    }

    public function test_can_show_order(): void
    {
        $order = Order::factory()->create([
            'customer_name' => 'Ricardo Saucedo',
            'customer_email' => 'ricardo@test.com',
            'total_amount' => 1500.50,
            'description' => 'Pedido de prueba',
            'status' => 'processed',
        ]);

        $response = $this->getJson("/api/orders/{$order->id}");

        $response->assertOk()
            ->assertJsonPath('data.id', $order->id)
            ->assertJsonPath('data.customer_name', 'Ricardo Saucedo')
            ->assertJsonPath('data.status', 'processed');
    }

    public function test_returns_404_when_order_does_not_exist(): void
    {
        $response = $this->getJson('/api/orders/999');

        $response->assertNotFound();
    }
}
