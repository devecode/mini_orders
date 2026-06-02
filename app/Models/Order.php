<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    protected $fillable = [
        'customer_name',
        'customer_email',
        'total_amount',
        'description',
        'status',
        'external_data',
        'error_message',
    ];
}
