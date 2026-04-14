using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace WorldAI.SDK.Models
{
    public class TileNode
    {
        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("faction_id")]
        public string FactionId { get; set; }
    }

    public class FactionDto
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }
        
        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("race_id")]
        public string RaceId { get; set; }

        [JsonPropertyName("population")]
        public int Population { get; set; }

        [JsonPropertyName("military_power")]
        public float MilitaryPower { get; set; }

        [JsonPropertyName("gold")]
        public float Gold { get; set; }
    }

    public class EventDto
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("description")]
        public string Description { get; set; }

        [JsonPropertyName("severity")]
        public int Severity { get; set; }
        
        [JsonPropertyName("affected_faction")]
        public string AffectedFaction { get; set; }
    }

    public class WsMessage
    {
        [JsonPropertyName("type")]
        public string Type { get; set; }

        // Data payload can be dynamically parsed depending on 'Type' (e.g. UPDATE, EVENT)
        [JsonPropertyName("data")]
        public object Data { get; set; }
    }
}
