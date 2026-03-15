import api from "./axiosConfig";
import type { Customer, Streak, BadgeList, LeaderboardList } from "../types";

export const getCustomerProfile = async(): Promise<Customer> => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};

export const getCustomerStreak = async () => {
  const response = await api.get<Streak>("/customers/streak");

  return response.data;
}

export const getOwnedBadges = async (): Promise<BadgeList> => {
  const response = await api.get<BadgeList>("/customers/badges/owned");
  return response.data;
};

export const getUnownedBadges = async (): Promise<BadgeList> => {
  const response = await api.get<BadgeList>("/customers/badges/unowned");
  return response.data;
};

export const getLeaderboard = async (): Promise<LeaderboardList> => {
  const response = await api.get<LeaderboardList>("/customers/leaderboard");
  return response.data;
};