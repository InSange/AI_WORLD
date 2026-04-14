using System;
using System.Net.Http;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Collections.Generic;

namespace WorldAI.SDK
{
    public class WorldAIClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly Uri _wsUri;
        private ClientWebSocket _webSocket;
        private CancellationTokenSource _cts;

        // Thread-safe message queue for Unity main-thread consumption
        private readonly ConcurrentQueue<string> _messageQueue;

        public WorldAIClient(string baseUrl = "http://localhost:8000")
        {
            _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl) };
            
            var wsUrl = baseUrl.Replace("http://", "ws://").Replace("https://", "wss://").TrimEnd('/');
            _wsUri = new Uri($"{wsUrl}/ws");
            _messageQueue = new ConcurrentQueue<string>();
        }

        /// <summary>
        /// Gets the current state of the world.
        /// </summary>
        public async Task<string> GetWorldAsync()
        {
            var response = await _httpClient.GetAsync("/world");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        /// <summary>
        /// Gets the data for all factions.
        /// </summary>
        public async Task<string> GetFactionsAsync()
        {
            var response = await _httpClient.GetAsync("/factions");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        /// <summary>
        /// Advances the simulation by specified hours.
        /// </summary>
        public async Task<string> TickAsync(int hours = 1)
        {
            var response = await _httpClient.PostAsync($"/simulation/tick?hours={hours}", null);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        /// <summary>
        /// Connects to the WebSocket and starts receiving real-time event updates into the concurrent queue.
        /// </summary>
        public async Task ConnectEventsAsync()
        {
            if (_webSocket != null && _webSocket.State == WebSocketState.Open)
                return;

            _webSocket = new ClientWebSocket();
            _cts = new CancellationTokenSource();

            await _webSocket.ConnectAsync(_wsUri, _cts.Token);
            _ = ReceiveMessagesAsync(); // Fire and forget the listening loop
        }

        private async Task ReceiveMessagesAsync()
        {
            var buffer = new byte[1024 * 16]; // 16KB buffer for delta updates
            try
            {
                while (_webSocket.State == WebSocketState.Open && !_cts.IsCancellationRequested)
                {
                    var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", _cts.Token);
                    }
                    else if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        _messageQueue.Enqueue(message);
                    }
                }
            }
            catch (OperationCanceledException)
            {
                // Normal closure
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[WorldAIClient] WebSocket Error: {ex.Message}");
            }
        }

        /// <summary>
        /// Consumes all received event messages from the background queue.
        /// Recommended to be called from Unity's Update() loop to process UI safely on the main thread.
        /// </summary>
        public IEnumerable<string> ConsumeEvents()
        {
            while (_messageQueue.TryDequeue(out var message))
            {
                yield return message;
            }
        }

        public void DisconnectEvents()
        {
            _cts?.Cancel();
            _webSocket?.Abort();
            _webSocket?.Dispose();
            _webSocket = null;
        }

        public void Dispose()
        {
            DisconnectEvents();
            _httpClient?.Dispose();
        }
    }
}
