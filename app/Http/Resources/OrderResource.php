<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class OrderResource extends JsonResource
{
    public function toArray($request): array
    {
        return [
            'id' => $this->id,
            'customer_name' => $this->customer_name,
            'customer_email' => $this->customer_email,
            'total_amount' => $this->total_amount,
            'description' => $this->description,
            'status' => $this->status,
            'external_data' => $this->external_data,
            'created_at' => $this->created_at,
        ];
    }
}
