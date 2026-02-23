#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# EduPlatform Demo Script — full user journey via curl + browser
# Prerequisites: docker compose dev running, seed data loaded, frontend on :3001
# Usage: ./tools/demo/demo.sh
# =============================================================================

IDENTITY=http://localhost:8001
COURSE=http://localhost:8002
ENROLLMENT=http://localhost:8003
PAYMENT=http://localhost:8004
NOTIFICATION=http://localhost:8005
FRONTEND=http://localhost:3001

DEMO_DELAY=${DEMO_DELAY:-1}
BROWSER_DELAY=${BROWSER_DELAY:-3}
TS=$(date +%s)
STEP_NUM=0

# Colors
Y='\033[1;33m'
G='\033[1;32m'
R='\033[1;31m'
C='\033[1;36m'
B='\033[1m'
N='\033[0m'

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

header() {
    echo ""
    echo -e "${Y}======================================================================${N}"
    echo -e "${Y}  $1${N}"
    echo -e "${Y}======================================================================${N}"
}

step() {
    STEP_NUM=$((STEP_NUM + 1))
    echo ""
    echo -e "${C}  [${STEP_NUM}] $1${N}"
}

pause() {
    sleep "$DEMO_DELAY"
}

# Open a URL in the browser (WSL2 → wslview, Linux → xdg-open, macOS → open)
browse() {
    local url="$1"
    local label="${2:-}"
    echo -e "  ${G}>>> Browser: ${url}${N}"
    if [[ -n "$label" ]]; then
        echo -e "  ${G}    ${label}${N}"
    fi
    if command -v wslview &>/dev/null; then
        wslview "$url" &>/dev/null &
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$url" &>/dev/null &
    elif command -v open &>/dev/null; then
        open "$url" &>/dev/null &
    fi
    sleep "$BROWSER_DELAY"
}

# call METHOD URL [DATA] [AUTH_TOKEN]
call() {
    local method="$1"
    local url="$2"
    local data="${3:-}"
    local token="${4:-}"

    local -a args=(-s -w '\n%{http_code}' -X "$method")
    args+=(-H 'Content-Type: application/json')

    if [[ -n "$token" ]]; then
        args+=(-H "Authorization: Bearer $token")
    fi
    if [[ -n "$data" ]]; then
        args+=(-d "$data")
    fi

    local raw
    raw=$(curl "${args[@]}" "$url")

    local http_code
    http_code=$(echo "$raw" | tail -1)
    local body
    body=$(echo "$raw" | sed '$d')

    echo -e "  ${B}${method} ${url}${N}  -> ${B}HTTP ${http_code}${N}"

    if [[ -n "$body" ]]; then
        echo "$body" | jq . 2>/dev/null || echo "$body"
    fi

    if [[ "$http_code" -lt 200 || "$http_code" -ge 300 ]]; then
        echo -e "${R}  FAILED (HTTP ${http_code}). Aborting.${N}"
        exit 1
    fi

    LAST_BODY="$body"
    LAST_CODE="$http_code"
    pause
}

extract_email_token() {
    docker compose -f docker-compose.dev.yml logs identity 2>&1 \
        | grep "\[EMAIL_VERIFY\]" | tail -1 | sed 's/.*token=//'
}

extract_reset_token() {
    docker compose -f docker-compose.dev.yml logs identity 2>&1 \
        | grep "\[PASSWORD_RESET\]" | tail -1 | sed 's/.*token=//'
}

jq_field() {
    echo "$LAST_BODY" | jq -r "$1"
}

# ---------------------------------------------------------------------------
# 0. Health check
# ---------------------------------------------------------------------------

header "0. Health Check — all services"

for svc_name in identity course enrollment payment notification; do
    case "$svc_name" in
        identity)     svc_url="$IDENTITY" ;;
        course)       svc_url="$COURSE" ;;
        enrollment)   svc_url="$ENROLLMENT" ;;
        payment)      svc_url="$PAYMENT" ;;
        notification) svc_url="$NOTIFICATION" ;;
    esac
    step "$svc_name /health/ready"
    call GET "${svc_url}/health/ready"
done

# ---------------------------------------------------------------------------
# 1. Student registration + email verification
# ---------------------------------------------------------------------------

STUDENT_EMAIL="demo-student-${TS}@test.com"
STUDENT_PASS="demo123"

header "1. Student Registration + Email Verification"

browse "$FRONTEND/register" "Opening registration page..."

step "Register student"
call POST "$IDENTITY/register" \
    "{\"email\":\"${STUDENT_EMAIL}\",\"password\":\"${STUDENT_PASS}\",\"name\":\"Demo Student\",\"role\":\"student\"}"
STUDENT_TOKEN=$(jq_field '.access_token')
STUDENT_REFRESH=$(jq_field '.refresh_token')

step "GET /me — email_verified should be false"
call GET "$IDENTITY/me" "" "$STUDENT_TOKEN"

step "Extract email verification token from Docker logs"
EMAIL_TOKEN=$(extract_email_token)
if [[ -z "$EMAIL_TOKEN" ]]; then
    echo -e "${R}  Could not extract email token from logs. Aborting.${N}"
    exit 1
fi
echo -e "  Token: ${B}${EMAIL_TOKEN}${N}"

step "Verify email"
call POST "$IDENTITY/verify-email" "{\"token\":\"${EMAIL_TOKEN}\"}"

browse "$FRONTEND/verify-email?token=${EMAIL_TOKEN}" "Opening email verification page..."

step "GET /me — email_verified should be true"
call GET "$IDENTITY/me" "" "$STUDENT_TOKEN"

# ---------------------------------------------------------------------------
# 2. Teacher registration + admin verification
# ---------------------------------------------------------------------------

TEACHER_EMAIL="demo-teacher-${TS}@test.com"
TEACHER_PASS="demo123"

header "2. Teacher Registration + Admin Verification"

step "Register teacher"
call POST "$IDENTITY/register" \
    "{\"email\":\"${TEACHER_EMAIL}\",\"password\":\"${TEACHER_PASS}\",\"name\":\"Demo Teacher\",\"role\":\"teacher\"}"
TEACHER_TOKEN=$(jq_field '.access_token')

step "GET /me — is_verified should be false"
call GET "$IDENTITY/me" "" "$TEACHER_TOKEN"
TEACHER_ID=$(jq_field '.id')

step "Login as admin"
call POST "$IDENTITY/login" \
    '{"email":"admin@eduplatform.com","password":"password"}'
ADMIN_TOKEN=$(jq_field '.access_token')

browse "$FRONTEND/admin/teachers" "Opening admin panel — pending teachers..."

step "GET /admin/teachers/pending"
call GET "$IDENTITY/admin/teachers/pending?limit=5" "" "$ADMIN_TOKEN"

step "PATCH /admin/users/${TEACHER_ID}/verify"
call PATCH "$IDENTITY/admin/users/${TEACHER_ID}/verify" "" "$ADMIN_TOKEN"

step "Re-login teacher to get fresh token with is_verified: true"
call POST "$IDENTITY/login" \
    "{\"email\":\"${TEACHER_EMAIL}\",\"password\":\"${TEACHER_PASS}\"}"
TEACHER_TOKEN=$(jq_field '.access_token')

step "GET /me — teacher verified"
call GET "$IDENTITY/me" "" "$TEACHER_TOKEN"

# ---------------------------------------------------------------------------
# 3. Teacher creates a course
# ---------------------------------------------------------------------------

header "3. Teacher Creates a Course"

step "GET /categories"
call GET "$COURSE/categories"
CATEGORY_ID=$(echo "$LAST_BODY" | jq -r '.[0].id')
CATEGORY_NAME=$(echo "$LAST_BODY" | jq -r '.[0].name')
echo -e "  Using category: ${B}${CATEGORY_NAME}${N} (${CATEGORY_ID})"

browse "$FRONTEND/courses/new" "Opening 'Create Course' page..."

step "POST /courses — create course"
call POST "$COURSE/courses" \
    "{\"title\":\"Demo Course ${TS}\",\"description\":\"A demo course for testing the platform\",\"is_free\":true,\"level\":\"beginner\",\"category_id\":\"${CATEGORY_ID}\"}" \
    "$TEACHER_TOKEN"
COURSE_ID=$(jq_field '.id')
echo -e "  Course ID: ${B}${COURSE_ID}${N}"

step "POST /courses/${COURSE_ID}/modules — Module 1"
call POST "$COURSE/courses/${COURSE_ID}/modules" \
    '{"title":"Getting Started","order":1}' \
    "$TEACHER_TOKEN"
MODULE1_ID=$(jq_field '.id')

step "POST /courses/${COURSE_ID}/modules — Module 2"
call POST "$COURSE/courses/${COURSE_ID}/modules" \
    '{"title":"Advanced Topics","order":2}' \
    "$TEACHER_TOKEN"
MODULE2_ID=$(jq_field '.id')

step "POST /modules/${MODULE1_ID}/lessons — Lesson 1"
call POST "$COURSE/modules/${MODULE1_ID}/lessons" \
    '{"title":"Introduction","content":"Welcome to the course!","duration_minutes":10,"order":1}' \
    "$TEACHER_TOKEN"
LESSON1_ID=$(jq_field '.id')

step "POST /modules/${MODULE1_ID}/lessons — Lesson 2"
call POST "$COURSE/modules/${MODULE1_ID}/lessons" \
    '{"title":"Setup Environment","content":"Install required tools","duration_minutes":15,"order":2}' \
    "$TEACHER_TOKEN"
LESSON2_ID=$(jq_field '.id')

step "POST /modules/${MODULE2_ID}/lessons — Lesson 3"
call POST "$COURSE/modules/${MODULE2_ID}/lessons" \
    '{"title":"Deep Dive","content":"Advanced concepts explained","duration_minutes":20,"order":1}' \
    "$TEACHER_TOKEN"
LESSON3_ID=$(jq_field '.id')

step "GET /courses/${COURSE_ID}/curriculum"
call GET "$COURSE/courses/${COURSE_ID}/curriculum"
TOTAL_LESSONS=$(jq_field '.total_lessons')
echo -e "  Total lessons: ${B}${TOTAL_LESSONS}${N}"

browse "$FRONTEND/courses/${COURSE_ID}" "Opening course page — see curriculum..."

# ---------------------------------------------------------------------------
# 4. Student takes the course
# ---------------------------------------------------------------------------

header "4. Student Takes the Course"

browse "$FRONTEND/courses?level=beginner&is_free=true" "Opening catalog — free beginner courses..."

step "GET /courses — filter free beginner courses"
call GET "$COURSE/courses?level=beginner&is_free=true&limit=5"

step "GET /courses/${COURSE_ID} — course details"
call GET "$COURSE/courses/${COURSE_ID}"

step "GET /enrollments/course/${COURSE_ID}/count — enrollment count before"
call GET "$ENROLLMENT/enrollments/course/${COURSE_ID}/count"

step "POST /enrollments — enroll in course"
call POST "$ENROLLMENT/enrollments" \
    "{\"course_id\":\"${COURSE_ID}\",\"total_lessons\":${TOTAL_LESSONS}}" \
    "$STUDENT_TOKEN"
ENROLLMENT_ID=$(jq_field '.id')

step "POST /notifications — enrollment notification"
call POST "$NOTIFICATION/notifications" \
    "{\"type\":\"enrollment\",\"title\":\"Enrolled in Demo Course\",\"body\":\"You have successfully enrolled!\"}" \
    "$STUDENT_TOKEN"
NOTIF_ID=$(jq_field '.id')

browse "$FRONTEND/enrollments" "Opening 'My Enrollments' page..."

step "GET /enrollments/me"
call GET "$ENROLLMENT/enrollments/me" "" "$STUDENT_TOKEN"

browse "$FRONTEND/courses/${COURSE_ID}/lessons/${LESSON1_ID}" "Opening Lesson 1..."

step "Complete lesson 1"
call POST "$ENROLLMENT/progress/lessons/${LESSON1_ID}/complete" \
    "{\"course_id\":\"${COURSE_ID}\"}" \
    "$STUDENT_TOKEN"

step "GET progress — should be ~33%"
call GET "$ENROLLMENT/progress/courses/${COURSE_ID}?total_lessons=${TOTAL_LESSONS}" "" "$STUDENT_TOKEN"

step "Complete lesson 2"
call POST "$ENROLLMENT/progress/lessons/${LESSON2_ID}/complete" \
    "{\"course_id\":\"${COURSE_ID}\"}" \
    "$STUDENT_TOKEN"

step "Complete lesson 3 — should trigger auto-completion"
call POST "$ENROLLMENT/progress/lessons/${LESSON3_ID}/complete" \
    "{\"course_id\":\"${COURSE_ID}\"}" \
    "$STUDENT_TOKEN"

step "GET progress — should be 100%"
call GET "$ENROLLMENT/progress/courses/${COURSE_ID}?total_lessons=${TOTAL_LESSONS}" "" "$STUDENT_TOKEN"

browse "$FRONTEND/enrollments" "Opening enrollments — course should be COMPLETED..."

step "GET /enrollments/me — status should be COMPLETED"
call GET "$ENROLLMENT/enrollments/me" "" "$STUDENT_TOKEN"

step "POST /reviews — leave a review"
call POST "$COURSE/reviews" \
    "{\"course_id\":\"${COURSE_ID}\",\"rating\":5,\"comment\":\"Excellent demo course!\"}" \
    "$STUDENT_TOKEN"

step "GET /reviews/course/${COURSE_ID}"
call GET "$COURSE/reviews/course/${COURSE_ID}"

browse "$FRONTEND/courses/${COURSE_ID}" "Opening course page — check rating and reviews..."

step "GET /courses/${COURSE_ID} — avg_rating should be updated"
call GET "$COURSE/courses/${COURSE_ID}"

# ---------------------------------------------------------------------------
# 5. Forgot password
# ---------------------------------------------------------------------------

header "5. Forgot Password Flow"

browse "$FRONTEND/forgot-password" "Opening forgot password page..."

step "POST /forgot-password"
call POST "$IDENTITY/forgot-password" "{\"email\":\"${STUDENT_EMAIL}\"}"

step "Extract reset token from Docker logs"
RESET_TOKEN=$(extract_reset_token)
if [[ -z "$RESET_TOKEN" ]]; then
    echo -e "${R}  Could not extract reset token from logs. Aborting.${N}"
    exit 1
fi
echo -e "  Token: ${B}${RESET_TOKEN}${N}"

browse "$FRONTEND/reset-password?token=${RESET_TOKEN}" "Opening reset password page..."

step "POST /reset-password"
call POST "$IDENTITY/reset-password" "{\"token\":\"${RESET_TOKEN}\",\"new_password\":\"newdemo123\"}"

step "POST /login with new password"
call POST "$IDENTITY/login" "{\"email\":\"${STUDENT_EMAIL}\",\"password\":\"newdemo123\"}"
STUDENT_TOKEN=$(jq_field '.access_token')
STUDENT_REFRESH=$(jq_field '.refresh_token')

# ---------------------------------------------------------------------------
# 6. Token refresh + logout
# ---------------------------------------------------------------------------

header "6. Token Refresh + Logout"

step "POST /refresh"
call POST "$IDENTITY/refresh" "{\"refresh_token\":\"${STUDENT_REFRESH}\"}"
STUDENT_TOKEN=$(jq_field '.access_token')
STUDENT_REFRESH=$(jq_field '.refresh_token')

step "POST /logout"
call POST "$IDENTITY/logout" "{\"refresh_token\":\"${STUDENT_REFRESH}\"}"

# ---------------------------------------------------------------------------
# 7. Catalog filters (bonus)
# ---------------------------------------------------------------------------

header "7. Catalog with Filters"

browse "$FRONTEND/courses?sort_by=avg_rating" "Opening catalog — sorted by rating..."

step "GET /courses — top rated"
call GET "$COURSE/courses?sort_by=avg_rating&limit=3"

browse "$FRONTEND/courses?q=Demo" "Opening catalog — search 'Demo'..."

step "GET /courses — search by keyword"
call GET "$COURSE/courses?q=Demo&limit=5"

step "GET /courses — filter by category + level"
call GET "$COURSE/courses?category_id=${CATEGORY_ID}&level=beginner&limit=5"

browse "$FRONTEND/notifications" "Opening notifications page..."

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo -e "${G}======================================================================${N}"
echo -e "${G}  Demo completed successfully!${N}"
echo -e "${G}  Student: ${STUDENT_EMAIL}${N}"
echo -e "${G}  Teacher: ${TEACHER_EMAIL}${N}"
echo -e "${G}  Course:  Demo Course ${TS} (${COURSE_ID})${N}"
echo -e "${G}======================================================================${N}"
echo ""
