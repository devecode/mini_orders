<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreOrderRequest;
use App\Models\Order;
use App\Http\Resources\OrderResource;
use App\Services\OrderService;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {
    }

    public function index()
    {
        return OrderResource::collection(Order::latest()->get());
    }

    public function store(StoreOrderRequest $request)
    {
        $order = $this->orderService->create(
            $request->validated()
        );

        return response()->json([
            'message' => 'Order created successfully',
            'data' => $order
        ], 201);
    }

    public function show(Order $order)
    {
        return new OrderResource($order);
    }
}
