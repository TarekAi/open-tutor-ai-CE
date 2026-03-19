import { TUTOR_API_BASE_URL } from '$lib/constants';

// --- Types ---
export interface AssignmentCreateRequest {
    title: string
    description: string
    classe_id: string
    deadline: Date
    points: number
}
export interface AssignmentResponse {
    id: string
    title: string
    description: string
    classe_id: string
    deadline: Date
    classe_name : string
    user_id: string;
    points: number
    created_at: string;
    updated_at: string;
    status: string
    max_submissions: number
    current_submissions: number
}


// ========== API Functions ========

// ---- create new assignment ----
export const createNewAssignment = async (token: string, data: AssignmentCreateRequest): Promise<AssignmentResponse> => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/assignment/create`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err.detail || "Failed to create assignment";
            console.error('Error creating assignment:', err);
            return null;
        });

    if (error) throw error;
    return res;
};

// --- get my assignment ---
export const getMyAssignment = async (token: string): Promise<AssignmentResponse[]> => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/assignment/all`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'authorization': `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err.detail || "Failed to fetch assignement";
            console.error('Error fetching Assignment:', err);
            return null;
        });
    if (error) throw error;
    return res;
};


// ---- update assignment ----
export const updateAssignment = async (token: string, assignmentId: string, data: AssignmentCreateRequest): Promise<AssignmentResponse> => {
    let error = null;
    const res = await fetch(`${TUTOR_API_BASE_URL}/assignment/${assignmentId}`, {
        method: 'PATCH',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err.detail || "Failed to update Assignment";
            console.error('Error updating Assignment:', err);
            return null;
        });

    if (error) throw error;
    return res;
};


// ---- delete assignment by id ----
export const deleteAssignmentById = async (token: string, assignmentId: string) => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/assignment/${assignmentId}`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err.detail || "Failed to delete Assignment";
            console.error('Error deleting Assignment:', err);
            return null;
        });

    if (error) throw error;
    return res;
};

// ---------------- Get Assignment Statistics ----------------
export const getAssignmentStats = async (token: string) => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/assignment/stats`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
};