using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Enhanced player data for the turn-based strategy game
/// Represents a single player's information and state
/// </summary>
[System.Serializable]
public class PlayerData
{
    public int playerID;
    public string playerName;
    public PlayerType playerType;
    public int teamID = -1; // -1 = no team
    public Color color;
    public bool isLocalPlayer = false; // For network play later
    public bool isEliminated = false;
    
    public bool IsAI()
    {
        return playerType != PlayerType.Human;
    }
    
    public bool IsOnTeam(int checkTeamID)
    {
        return teamID == checkTeamID;
    }
}

/// <summary>
/// Team data for team-based game modes
/// Manages team composition and state
/// </summary>
[System.Serializable]
public class TeamData
{
    public int teamID;
    public string teamName;
    public Color teamColor;
    public bool isEliminated = false;
    public List<int> memberPlayerIDs = new List<int>();
}

