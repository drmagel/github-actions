/**
 * Version Manager UI - Modal Components
 */

const { useState, useEffect } = React;

// Confirmation Modal
const ConfirmModal = ({ isOpen, title, message, onConfirm, onCancel }) => {
    if (!isOpen) return null;
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3 className="modal-title">{title}</h3>
                </div>
                <div className="modal-body">
                    <p>{message}</p>
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
                    <button className="btn btn-danger" onClick={onConfirm}>OK</button>
                </div>
            </div>
        </div>
    );
};

// Success Modal
const SuccessModal = ({ isOpen, message, onClose }) => {
    useEffect(() => {
        if (isOpen) {
            const timer = setTimeout(onClose, 1500);
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    if (!isOpen) return null;
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal success-modal" onClick={(e) => e.stopPropagation()}>
                <div className="success-icon">✓</div>
                <p>{message}</p>
            </div>
        </div>
    );
};

// Form Modal
const FormModal = ({ isOpen, title, children, onClose, onSubmit, className }) => {
    if (!isOpen) return null;
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className={`modal ${className || ''}`} onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3 className="modal-title">{title}</h3>
                    <button className="btn-close" onClick={onClose}>×</button>
                </div>
                <form onSubmit={onSubmit}>
                    <div className="modal-body">{children}</div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Submit</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

// Badge Component
const Badge = ({ type, children }) => {
    const classMap = {
        dev: 'badge-info',
        staging: 'badge-warning',
        prod: 'badge-success',
        tested: 'badge-success',
        active: 'badge-success',
        default: 'badge-secondary'
    };
    return <span className={`badge ${classMap[type] || classMap.default}`}>{children}</span>;
};

