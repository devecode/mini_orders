<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

class OrderFactory extends Factory
{
    public function definition(): array
    {
        return [
            'customer_name' => fake()->name(),
            'customer_email' => fake()->safeEmail(),
            'total_amount' => fake()->randomFloat(2, 1, 5000),
            'description' => fake()->sentence(),
            'status' => 'pending',
            'external_data' => null,
            'error_message' => null,
        ];
    }
}
