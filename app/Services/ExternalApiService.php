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
            ->get('https://api.github.com/zen');

        if ($response->failed()) {
            throw new \Exception('External API request failed.');
        }

        return $response->body();
    }
}
