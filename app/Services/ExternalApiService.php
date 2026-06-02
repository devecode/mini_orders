<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class ExternalApiService
{
    public function getExternalData(): string
    {
        $response = Http::timeout(10)
            ->withHeaders([
                'User-Agent' => 'Laravel Mini Orders'
            ])
            ->get(config('services.external_api.url'));

        if ($response->failed()) {
            throw new \Exception('External API request failed.');
        }

        return $response->body();
    }
}
