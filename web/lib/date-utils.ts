/**
 * Date utility functions
 */

/**
 * Format a date as distance to now (e.g., "2 hours ago", "3 days ago")
 *
 * @param date - The date to format
 * @returns Formatted string showing relative time
 */
export function formatDistanceToNow(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)
  const diffMonths = Math.floor(diffDays / 30)
  const diffYears = Math.floor(diffDays / 365)

  if (diffSeconds < 60) {
    return "just now"
  } else if (diffMinutes < 60) {
    return `${diffMinutes} ${diffMinutes === 1 ? "minute" : "minutes"} ago`
  } else if (diffHours < 24) {
    return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`
  } else if (diffDays === 1) {
    return "yesterday"
  } else if (diffDays < 30) {
    return `${diffDays} days ago`
  } else if (diffMonths < 12) {
    return `${diffMonths} ${diffMonths === 1 ? "month" : "months"} ago`
  } else {
    return `${diffYears} ${diffYears === 1 ? "year" : "years"} ago`
  }
}

/**
 * Format a date as a readable string
 *
 * @param date - The date to format
 * @returns Formatted string (e.g., "Jan 15, 2024")
 */
export function formatDate(date: Date): string {
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ]

  const month = months[date.getMonth()]
  const day = date.getDate()
  const year = date.getFullYear()

  return `${month} ${day}, ${year}`
}
